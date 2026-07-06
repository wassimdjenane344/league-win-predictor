"""Metric computation and the quality-gate decision used by the promotion pipeline."""

from __future__ import annotations

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

# Minimum accuracy required to promote staging -> production.
# Other metrics are logged for visibility and can be gated on later.
ACCURACY_THRESHOLD = 0.70


def compute_metrics(y_true, y_pred, y_proba) -> dict:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_score": f1_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "roc_auc": roc_auc_score(y_true, y_proba),
    }


def passes_quality_gate(metrics: dict) -> bool:
    """Minimum accuracy gate on the held-out test set. False leaves the model
    in "Staging" -- the caller (ml/src/promote.py) never touches "Production".
    """
    return metrics["accuracy"] >= ACCURACY_THRESHOLD
