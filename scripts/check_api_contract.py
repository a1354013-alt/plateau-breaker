from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, cwd: Path) -> None:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify frontend generated API types match backend OpenAPI schema.",
    )
    parser.add_argument(
        "--write-openapi-json",
        action="store_true",
        help="Also write frontend/openapi.json for local inspection (not required for CI).",
    )
    args = parser.parse_args()

    repo = _repo_root()
    frontend_dir = repo / "frontend"
    export_script = repo / "scripts" / "export_openapi.py"
    generated_types = frontend_dir / "src" / "generated" / "api.ts"

    if not generated_types.exists():
        sys.stderr.write(f"Missing generated types: {generated_types}\n")
        sys.stderr.write("Run: python scripts/export_openapi.py --out frontend/openapi.json\n")
        sys.stderr.write("Then: npm --prefix frontend run generate:api\n")
        return 1

    bin_name = "openapi-typescript.cmd" if os.name == "nt" else "openapi-typescript"
    openapi_typescript_bin = frontend_dir / "node_modules" / ".bin" / bin_name
    if not openapi_typescript_bin.exists():
        sys.stderr.write("Missing openapi-typescript binary. Run `npm ci` in frontend first.\n")
        return 1

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        openapi_json = tmp / "openapi.json"
        tmp_types = tmp / "api.ts"

        _run([sys.executable, str(export_script), "--out", str(openapi_json)], cwd=repo)
        _run([str(openapi_typescript_bin), str(openapi_json), "-o", str(tmp_types)], cwd=frontend_dir)

        expected = tmp_types.read_text(encoding="utf-8")
        actual = generated_types.read_text(encoding="utf-8")
        if expected != actual:
            sys.stderr.write("API contract drift detected: frontend/src/generated/api.ts is out of date.\n")
            sys.stderr.write("Regenerate with:\n")
            sys.stderr.write("  python scripts/export_openapi.py --out frontend/openapi.json\n")
            sys.stderr.write("  npm --prefix frontend run generate:api\n")
            return 1

        if args.write_openapi_json:
            _run([sys.executable, str(export_script), "--out", str(frontend_dir / "openapi.json")], cwd=repo)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
