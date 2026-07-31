from pathlib import Path


def test_dockerfile_defines_railway_api_runtime() -> None:
    dockerfile = Path(__file__).resolve().parents[1] / "Dockerfile"

    assert dockerfile.is_file()

    content = dockerfile.read_text(encoding="utf-8")
    assert "FROM python:3.12-slim" in content
    assert "PYTHONDONTWRITEBYTECODE=1" in content
    assert "PYTHONUNBUFFERED=1" in content
    assert "PIP_NO_CACHE_DIR=1" in content
    assert "WORKDIR /app" in content
    assert "COPY pyproject.toml ./" in content
    assert "COPY app ./app" in content
    assert "COPY alembic ./alembic" in content
    assert "COPY alembic.ini ./" in content
    assert "pip install --upgrade pip" in content
    assert "pip install ." in content
    assert "EXPOSE 8000" in content
    assert "uvicorn app.main:app" in content
    assert "--host 0.0.0.0" in content
    assert "${PORT:-8000}" in content
    assert "alembic upgrade" not in content


def test_dockerignore_excludes_local_artifacts_and_environment_files() -> None:
    dockerignore = Path(__file__).resolve().parents[1] / ".dockerignore"

    assert dockerignore.is_file()
    assert dockerignore.read_text(encoding="utf-8").splitlines() == [
        ".venv/",
        ".pytest_cache/",
        "__pycache__/",
        "*.py[cod]",
        "tests/",
        "storage/",
        ".env*",
    ]
    assert "!.env.example" not in dockerignore.read_text(encoding="utf-8")
