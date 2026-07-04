"""Loads the win-prediction model straight from the MLflow Model Registry.

The final project spec is explicit that "the registry is the single source
of truth for deployments" and that "production must serve predictions from
the Production registry stage only". This module never reads a model file
from disk: it always resolves `models:/<name>/<stage>` through MLflow, where
`<stage>` is `Staging` in the staging environment and `Production` in
production (see backend/app/config.py, driven by the MLFLOW_MODEL_STAGE
env var so the same Docker image is used in both environments).
"""

from __future__ import annotations

import logging
import os
import threading

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.tracking import MlflowClient

from .features import FEATURE_COLUMNS

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_state: dict = {"model": None, "version": None, "run_id": None, "tags": {}}

# Read directly from the environment (rather than through app.config.Config)
# on every call, not just at import time: this is what lets each gunicorn
# worker -- and each test, via monkeypatch.setenv -- point at its own MLflow
# registry/stage without stale values cached from process start.


def _model_name() -> str:
    return os.environ.get("MLFLOW_MODEL_NAME", "lol-win-predictor")


def _model_stage() -> str:
    return os.environ.get("MLFLOW_MODEL_STAGE", "Production")


def _configure_mlflow() -> None:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)


def load_model(force_reload: bool = False):
    """Load (and cache) the model currently in the configured registry stage.

    Thread-safe so it can be called lazily on the first request of a
    gunicorn worker without loading the model multiple times concurrently.
    """
    with _lock:
        if _state["model"] is not None and not force_reload:
            return _state["model"]

        _configure_mlflow()
        model_name, model_stage = _model_name(), _model_stage()
        client = MlflowClient()
        versions = client.get_latest_versions(model_name, stages=[model_stage])
        if not versions:
            raise RuntimeError(
                f"No model version found in stage '{model_stage}' "
                f"for registered model '{model_name}'."
            )
        mv = versions[0]
        model_uri = f"models:/{model_name}/{model_stage}"
        model = mlflow.sklearn.load_model(model_uri)

        run = client.get_run(mv.run_id)
        _state.update(
            model=model,
            version=mv.version,
            run_id=mv.run_id,
            model_name=model_name,
            model_stage=model_stage,
            tags={
                "git_commit": run.data.tags.get("git_commit", "unknown"),
                "dvc_data_version": run.data.tags.get("dvc_data_version", "unknown"),
            },
        )
        logger.info(
            "Loaded %s v%s (stage=%s, run=%s)", model_name, mv.version, model_stage, mv.run_id
        )
        return model


def model_metadata() -> dict:
    return {
        "model_name": _state.get("model_name", _model_name()),
        "model_stage": _state.get("model_stage", _model_stage()),
        "model_version": _state["version"],
        "training_run_id": _state["run_id"],
        "git_commit": _state["tags"].get("git_commit"),
        "dvc_data_version": _state["tags"].get("dvc_data_version"),
    }


def predict_win_probability(feature_vector: list[float]) -> float:
    model = load_model()
    row = pd.DataFrame([feature_vector], columns=FEATURE_COLUMNS)
    proba = model.predict_proba(row)[0]
    # class "1" (index 1) is blueWins == 1, see ml/src/features.py TARGET_COLUMN
    return float(proba[1])
