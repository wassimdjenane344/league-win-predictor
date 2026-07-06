"""12-factor configuration: environment-specific values come from the
environment, never hard-coded. Injected from GitHub Environment Secrets in
CI/CD (see .github/workflows/*.yml); from a .env file locally (.env.example).
"""

from __future__ import annotations

import os


class Config:
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")

    # MLFLOW_TRACKING_URI / MLFLOW_MODEL_NAME / MLFLOW_MODEL_STAGE are read
    # directly from os.environ in model_loader.py instead of cached here, so
    # each gunicorn worker (and each test, via monkeypatch.setenv) always
    # sees the current value.

    # Networking
    PORT: int = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")

    # Traceability: which commit built this image (set at build/deploy time)
    GIT_COMMIT: str = os.environ.get("GIT_COMMIT", "unknown")
    APP_VERSION: str = os.environ.get("APP_VERSION", "0.1.0")

    @classmethod
    def as_dict(cls) -> dict:
        return {
            k: v
            for k, v in vars(cls).items()
            if k.isupper()
        }
