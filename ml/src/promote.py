"""Model promotion pipeline: Staging candidate -> quality gate -> Production.

This is the "Model Promotion Pipeline (Core Requirement)" from the final
project spec. It is meant to run as the last step of the `staging` ->
`main` GitHub Actions workflow:

    1. Fetch the current "Staging" model version (the candidate the
       dev->staging pipeline deployed).
    2. Re-evaluate it against a held-out split of the reference dataset
       (the required quality gate; here: minimum accuracy).
    3. If the gate passes: promote the version to "Production" and
       archive the previous Production version.
       If it fails: leave Staging untouched, change nothing in
       Production, and exit with a non-zero status so the CI job -- and
       therefore the staging->main merge -- fails.

Usage:
    python ml/src/promote.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient
from sklearn.model_selection import train_test_split

from evaluate import compute_metrics, passes_quality_gate
from features import FEATURE_COLUMNS, TARGET_COLUMN

ML_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ML_DIR / "data" / "raw" / "high_diamond_ranked_10min.csv"
MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME", "lol-win-predictor")


def get_staging_version(client: MlflowClient):
    versions = client.get_latest_versions(MODEL_NAME, stages=["Staging"])
    if not versions:
        raise SystemExit(
            f"No model version currently in Staging for '{MODEL_NAME}'. "
            "Run train.py --register first."
        )
    return versions[0]


def main() -> None:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", (ML_DIR / "mlruns").resolve().as_uri())
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    candidate = get_staging_version(client)
    print(f"Candidate: {MODEL_NAME} v{candidate.version} (run {candidate.run_id})")

    model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/{candidate.version}")

    df = pd.read_csv(DEFAULT_DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    # Same seed/split as training so the gate is evaluated on a comparable holdout.
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    metrics = compute_metrics(y_test, y_pred, y_proba)
    print("Quality gate metrics:", metrics)

    if passes_quality_gate(metrics):
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=candidate.version,
            stage="Production",
            archive_existing_versions=True,
        )
        print(f"PASS: promoted {MODEL_NAME} v{candidate.version} to Production")
    else:
        print(
            f"FAIL: accuracy {metrics['accuracy']:.4f} is below the "
            f"required threshold. Model stays in Staging, Production unchanged."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
