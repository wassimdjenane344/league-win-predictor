"""Unit test #2: the promotion quality gate (ml/src/evaluate.py).

This is the function that decides whether a candidate model may move from
"Staging" to "Production" (see ml/src/promote.py) -- getting the threshold
comparison wrong would silently let a bad model reach production, so it is
tested directly against the ACCURACY_THRESHOLD constant rather than against
a hard-coded number.
"""

from evaluate import ACCURACY_THRESHOLD, passes_quality_gate


def test_passes_quality_gate_when_accuracy_meets_threshold():
    metrics = {"accuracy": ACCURACY_THRESHOLD}

    assert passes_quality_gate(metrics) is True


def test_fails_quality_gate_when_accuracy_below_threshold():
    metrics = {"accuracy": ACCURACY_THRESHOLD - 0.01}

    assert passes_quality_gate(metrics) is False
