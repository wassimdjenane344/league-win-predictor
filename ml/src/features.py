"""Feature schema shared by training and serving.

Uses the *blue-side* subset of the raw Kaggle columns (dataset: "League of
Legends Diamond Ranked Games (10 min)") -- the stats a player can read off
their own scoreboard at minute 10.
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

TARGET_COLUMN = "blueWins"

# Roughly the dataset median, so the API/frontend can omit fields.
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
    """Turn a (possibly partial) JSON payload into an ordered feature vector."""
    return [float(payload.get(col, FEATURE_DEFAULTS[col])) for col in FEATURE_COLUMNS]
