from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_app():
    repo_root = Path(__file__).resolve().parents[1]
    backend_dir = repo_root / "backend"
    sys.path.insert(0, str(backend_dir))

    from app.main import app  # noqa: WPS433 (runtime import for script)

    return app


def main() -> int:
    parser = argparse.ArgumentParser(description="Export PlateauBreaker backend OpenAPI schema as JSON.")
    parser.add_argument("--out", type=Path, default=None, help="Output path (default: stdout).")
    args = parser.parse_args()

    app = _load_app()
    schema = app.openapi()
    payload = json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True)

    if args.out is None:
        sys.stdout.write(payload)
        return 0

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

