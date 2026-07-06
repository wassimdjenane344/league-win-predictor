"""Tests for the promotion quality gate (ml/src/evaluate.py).

Checked against the ACCURACY_THRESHOLD constant rather than a hard-coded
number, so it stays correct if the threshold changes.
"""

from evaluate import ACCURACY_THRESHOLD, passes_quality_gate


def test_passes_quality_gate_when_accuracy_meets_threshold():
    metrics = {"accuracy": ACCURACY_THRESHOLD}

    assert passes_quality_gate(metrics) is True


def test_fails_quality_gate_when_accuracy_below_threshold():
    metrics = {"accuracy": ACCURACY_THRESHOLD - 0.01}

    assert passes_quality_gate(metrics) is False
