"""Metric computation and the quality-gate decision used by the promotion pipeline."""

from __future__ import annotations

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

# Quality gate thresholds for staging -> production promotion.
# accuracy is the primary gate required by the project spec; the others
# are logged for visibility and can be tightened later.
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
    """The single required quality gate: minimum accuracy on the held-out test set.

    Returning False must leave the model in "Staging" and must not touch
    "Production" -- enforced by the caller (ml/src/promote.py).
    """
    return metrics["accuracy"] >= ACCURACY_THRESHOLD
