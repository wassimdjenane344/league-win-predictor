"""Feature contract for the /predict endpoint.

Kept as a standalone copy of ml/src/features.py rather than a shared import,
since backend/ and ml/ are built and deployed as separate Docker images.
tests/unit/test_features.py catches it if the two ever drift apart.
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
