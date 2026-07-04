"""Shared pytest fixtures.

The integration tests need a real MLflow Model Registry with a model in
"Production" to exercise the actual backend code path (no mocking of
MLflow itself: this is what makes them integration tests rather than unit
tests). Instead of depending on a shared/external MLflow server, each test
session gets its own throwaway registry, trained and promoted through the
*real* ml/src/train.py and ml/src/promote.py scripts -- so a green test
suite is also proof that the training + promotion pipeline itself works.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ML_SRC = REPO_ROOT / "ml" / "src"


@pytest.fixture(scope="session")
def trained_registry_uri(tmp_path_factory):
    tracking_dir = tmp_path_factory.mktemp("mlruns")
    tracking_uri = tracking_dir.as_uri()
    env = {
        **os.environ,
        "MLFLOW_TRACKING_URI": tracking_uri,
        "MLFLOW_MODEL_NAME": "lol-win-predictor",
    }

    subprocess.run(
        [sys.executable, "train.py", "--model-type", "logreg", "--register"],
        cwd=ML_SRC,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, "promote.py"],
        cwd=ML_SRC,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return tracking_uri


@pytest.fixture()
def flask_app(trained_registry_uri, monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", trained_registry_uri)
    monkeypatch.setenv("MLFLOW_MODEL_NAME", "lol-win-predictor")
    monkeypatch.setenv("MLFLOW_MODEL_STAGE", "Production")

    from app import create_app
    from app.model_loader import load_model

    application = create_app()
    load_model(force_reload=True)  # ensure it picks up this test's registry
    return application


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()
