from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import zipfile


REQUIRED_FRONTEND_DIST_FILES = ("index.html",)


@dataclass(frozen=True)
class ReleasePaths:
    root: Path
    backend: Path
    frontend_dist: Path
    readme: Path
    technical_guide: Path
    env_example: Path
    dockerfile: Path
    docker_compose: Path


def repo_paths() -> ReleasePaths:
    root = Path(__file__).resolve().parents[1]
    return ReleasePaths(
        root=root,
        backend=root / "backend",
        frontend_dist=root / "frontend" / "dist",
        readme=root / "README.md",
        technical_guide=root / "PlateauBreaker_Technical_Guide.md",
        env_example=root / ".env.example",
        dockerfile=root / "Dockerfile",
        docker_compose=root / "docker-compose.yml",
    )


def _should_exclude_dir(name: str) -> bool:
    return name in {
        ".git",
        ".idea",
        ".vscode",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "dist-ssr",
        ".npm-cache",
        "release",
        "release_tmp",
        "tests",
        "data",
    }


def _should_exclude_file(name: str) -> bool:
    lowered = name.lower()
    if lowered.endswith((".pyc", ".pyo", ".pyd", ".log", ".tmp", ".swp")):
        return True
    if lowered.endswith((".db", ".sqlite", ".sqlite3")):
        return True
    if lowered in {"requirements-dev.txt", "pytest.ini"}:
        return True
    if lowered == ".env" or lowered.startswith(".env."):
        return True
    return False


def add_tree(zf: zipfile.ZipFile, *, src: Path, dest_prefix: str) -> None:
    for p in src.rglob("*"):
        rel = p.relative_to(src)

        if p.is_dir():
            if _should_exclude_dir(p.name):
                # Skip entire subtree.
                continue
            continue

        # Exclude if any parent dir is excluded.
        if any(_should_exclude_dir(part) for part in rel.parts):
            continue

        if _should_exclude_file(p.name):
            continue

        arcname = str(Path(dest_prefix) / rel).replace("\\", "/")
        zf.write(p, arcname)


def ensure_frontend_dist_ready(frontend_dist: Path) -> None:
    if not frontend_dist.exists():
        raise SystemExit(
            f"Missing frontend build output: {frontend_dist}. Run: cd frontend && npm ci && npm run build"
        )
    missing = [f for f in REQUIRED_FRONTEND_DIST_FILES if not (frontend_dist / f).exists()]
    if missing:
        raise SystemExit(f"frontend/dist is missing required file(s): {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a clean, deployable PlateauBreaker release zip.")
    parser.add_argument("--out-dir", default="release", help="Output directory (relative to repo root).")
    args = parser.parse_args()

    paths = repo_paths()
    ensure_frontend_dist_ready(paths.frontend_dist)

    out_dir = (paths.root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = out_dir / f"PlateauBreaker_release_{timestamp}.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        add_tree(zf, src=paths.backend, dest_prefix="backend")
        add_tree(zf, src=paths.frontend_dist, dest_prefix="frontend/dist")
        zf.write(paths.readme, "README.md")
        if paths.technical_guide.exists():
            zf.write(paths.technical_guide, paths.technical_guide.name)
        if paths.env_example.exists():
            zf.write(paths.env_example, paths.env_example.name)
        if paths.dockerfile.exists():
            zf.write(paths.dockerfile, paths.dockerfile.name)
        if paths.docker_compose.exists():
            zf.write(paths.docker_compose, paths.docker_compose.name)

    print(f"Created: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
