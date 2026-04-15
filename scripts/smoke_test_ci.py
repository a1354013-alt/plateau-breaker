from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]


def _http_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, {"_error": raw}


def _http_text(url: str) -> tuple[int, str]:
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, raw
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, raw


def _wait_for(url: str, *, timeout_s: int = 30) -> None:
    start = time.time()
    while True:
        try:
            status, _ = _http_json("GET", url)
            if status == 200:
                return
        except URLError:
            pass

        if time.time() - start > timeout_s:
            raise RuntimeError(f"Timed out waiting for {url}")
        time.sleep(0.25)


def _terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return

    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
        proc.wait(timeout=10)


def main() -> int:
    backend_url = "http://127.0.0.1:8000"
    frontend_url = "http://127.0.0.1:4173"

    dist_dir = REPO_ROOT / "frontend" / "dist"
    if not dist_dir.exists():
        raise SystemExit("frontend/dist not found. Run `npm --prefix frontend run build` first.")

    db_path = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "plateaubreaker_integration.sqlite3"
    if db_path.exists():
        db_path.unlink()

    backend_env = os.environ.copy()
    backend_env["PLATEAUBREAKER_DB_PATH"] = str(db_path)
    backend_env.setdefault("APP_TIMEZONE", "Asia/Taipei")

    backend_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            "backend",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=str(REPO_ROOT),
        env=backend_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "4173", "--directory", str(dist_dir)],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        _wait_for(f"{backend_url}/health")

        # Create one record safely in the past (timezone-agnostic)
        record_date = (date.today() - timedelta(days=1)).isoformat()
        status, payload = _http_json(
            "POST",
            f"{backend_url}/api/health-records",
            {
                "record_date": record_date,
                "weight": 75.0,
                "sleep_hours": 7.0,
                "calories": 2000,
                "protein": 120,
                "exercise_minutes": 30,
                "exercise_type": "Walking",
                "steps": 8000,
                "note": "smoke",
            },
        )
        assert status == 201, payload
        assert str(payload.get("created_at", "")).endswith("Z")
        assert str(payload.get("updated_at", "")).endswith("Z")

        status, payload = _http_json("GET", f"{backend_url}/api/health-records")
        assert status == 200, payload
        assert payload.get("total", 0) >= 1

        status, payload = _http_json("GET", f"{backend_url}/api/analytics/summary?calorie_target=2000")
        assert status == 200, payload
        assert "summary" in payload and "plateau" in payload and "reasons" in payload

        # Frontend dist is servable
        status, body = _http_text(f"{frontend_url}/")
        assert status == 200
        assert "<title>" in body
    finally:
        _terminate(frontend_proc)
        _terminate(backend_proc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

