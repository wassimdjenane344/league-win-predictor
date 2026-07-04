"""Feature contract for the /predict endpoint.

Deliberately kept as a small, self-contained copy of ml/src/features.py
rather than a shared import across the ml/ and backend/ Docker build
contexts: the two services are built and deployed independently (each
with its own Dockerfile and its own requirements.txt), and this contract
is a short, stable list of column names, not logic worth the added
cross-context import wiring. If it drifts, the unit tests in
tests/unit/test_features.py catch it.
"""

from __future__ import annotations

FEATURE_COLUMNS: list[str] = [
    "blueWardsPlaced",
    "blueWardsDestroyed",
    "blueFirstBlood",
    "blueKills",
    "blueDeaths",
    "blueAssists",
    "blueDragons",
    "blueHeralds",
    "blueTowersDestroyed",
    "blueTotalGold",
    "blueAvgLevel",
    "blueTotalExperience",
    "blueTotalMinionsKilled",
    "blueGoldDiff",
    "blueExperienceDiff",
    "blueCSPerMin",
    "blueGoldPerMin",
]

FEATURE_DEFAULTS: dict[str, float] = {
    "blueWardsPlaced": 14,
    "blueWardsDestroyed": 2,
    "blueFirstBlood": 0,
    "blueKills": 6,
    "blueDeaths": 6,
    "blueAssists": 6,
    "blueDragons": 0,
    "blueHeralds": 0,
    "blueTowersDestroyed": 0,
    "blueTotalGold": 16500,
    "blueAvgLevel": 6.9,
    "blueTotalExperience": 17900,
    "blueTotalMinionsKilled": 216,
    "blueGoldDiff": 0,
    "blueExperienceDiff": 0,
    "blueCSPerMin": 21.6,
    "blueGoldPerMin": 1650,
}


def build_feature_vector(payload: dict) -> list[float]:
    return [float(payload.get(col, FEATURE_DEFAULTS[col])) for col in FEATURE_COLUMNS]
