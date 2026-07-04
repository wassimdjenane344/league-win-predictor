"""Unit test #1: feature-vector construction (backend/app/features.py).

Pure function, no network/model/file I/O -- this is what makes it a unit
test rather than an integration test.
"""

from app.features import FEATURE_COLUMNS, FEATURE_DEFAULTS, build_feature_vector


def test_build_feature_vector_uses_defaults_for_missing_fields():
    vector = build_feature_vector({})

    assert len(vector) == len(FEATURE_COLUMNS)
    assert vector == [float(FEATURE_DEFAULTS[col]) for col in FEATURE_COLUMNS]


def test_build_feature_vector_overrides_only_the_provided_fields():
    partial_payload = {"blueGoldDiff": 2500, "blueKills": 10}

    vector = build_feature_vector(partial_payload)

    as_dict = dict(zip(FEATURE_COLUMNS, vector, strict=True))
    assert as_dict["blueGoldDiff"] == 2500.0
    assert as_dict["blueKills"] == 10.0
    # Everything else must still fall back to the dataset-median default.
    assert as_dict["blueDeaths"] == float(FEATURE_DEFAULTS["blueDeaths"])
