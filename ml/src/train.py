"""Train the League of Legends 10-minute win predictor and log everything to MLflow.

Each run logs params, metrics, the DVC data version, and the Git commit hash.
With --register, the model is registered and moved to the "Staging" stage,
where ml/src/promote.py can later pick it up for the quality gate.

Usage:
    python ml/src/train.py --model-type logreg --register
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from evaluate import compute_metrics
from features import FEATURE_COLUMNS, TARGET_COLUMN
from versioning import get_dvc_data_version, get_git_commit

ML_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ML_DIR / "data" / "raw" / "high_diamond_ranked_10min.csv"
DEFAULT_DVC_FILE = ML_DIR / "data" / "raw" / "high_diamond_ranked_10min.csv.dvc"

MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME", "lol-win-predictor")


def build_model(model_type: str, **params):
    if model_type == "logreg":
        clf = LogisticRegression(max_iter=1000, C=params.get("C", 1.0))
    elif model_type == "random_forest":
        clf = RandomForestClassifier(
            n_estimators=params.get("n_estimators", 200),
            max_depth=params.get("max_depth", 6),
            random_state=42,
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    return Pipeline([("scaler", StandardScaler()), ("clf", clf)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--model-type", choices=["logreg", "random_forest"], default="logreg")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--C", type=float, default=1.0)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--register", action="store_true", help="Register model version and move it to Staging"
    )
    args = parser.parse_args()

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", (ML_DIR / "mlruns").resolve().as_uri())
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(os.environ.get("MLFLOW_EXPERIMENT_NAME", "lol-win-predictor"))

    df = pd.read_csv(args.data)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )

    model = build_model(
        args.model_type, C=args.C, n_estimators=args.n_estimators, max_depth=args.max_depth
    )

    with mlflow.start_run() as run:
        mlflow.log_params(
            {
                "model_type": args.model_type,
                "test_size": args.test_size,
                "seed": args.seed,
                "C": args.C if args.model_type == "logreg" else None,
                "n_estimators": args.n_estimators if args.model_type == "random_forest" else None,
                "max_depth": args.max_depth if args.model_type == "random_forest" else None,
                "n_rows": len(df),
                "n_features": len(FEATURE_COLUMNS),
            }
        )

        git_commit = get_git_commit()
        dvc_data_version = get_dvc_data_version(DEFAULT_DVC_FILE)
        mlflow.set_tags(
            {
                "git_commit": git_commit,
                "dvc_data_version": dvc_data_version,
                "dataset": "high_diamond_ranked_10min.csv",
            }
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        metrics = compute_metrics(y_test, y_pred, y_proba)
        mlflow.log_metrics(metrics)

        print(f"Run {run.info.run_id} | commit={git_commit[:8]} | data={dvc_data_version[:8]}")
        print("Metrics:", metrics)

        if args.register:
            model_info = mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=MODEL_NAME,
                input_example=X_train.head(2),
            )
            client = MlflowClient()
            version = model_info.registered_model_version
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=version,
                stage="Staging",
                archive_existing_versions=False,
            )
            client.update_model_version(
                name=MODEL_NAME,
                version=version,
                description=(
                    f"Candidate trained from commit {git_commit[:8]} "
                    f"on data version {dvc_data_version[:8]}. "
                    f"accuracy={metrics['accuracy']:.4f}"
                ),
            )
            print(f"Registered {MODEL_NAME} v{version} and moved it to Staging")
        else:
            mlflow.sklearn.log_model(model, artifact_path="model")


if __name__ == "__main__":
    main()
