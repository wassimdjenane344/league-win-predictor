"""12-factor configuration: every environment-specific value comes from the
environment (never hard-coded), as required by the "12-Factor App" section
of the final project spec. In CI/CD these variables are injected from
GitHub Environment Secrets (see .github/workflows/*.yml); locally they come
from a .env file (see .env.example at the repo root).
"""

from __future__ import annotations

import os


class Config:
    # Which environment this process is running as: development | staging | production
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")

    # Note: MLFLOW_TRACKING_URI / MLFLOW_MODEL_NAME / MLFLOW_MODEL_STAGE are
    # deliberately NOT cached here. app/model_loader.py reads them straight
    # from os.environ on every call, so each gunicorn worker (and each test,
    # via monkeypatch.setenv) always sees the current value rather than
    # whatever was in the environment when this class body first ran.

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
