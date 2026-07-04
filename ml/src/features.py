"""Feature schema shared by training and serving.

Keeping this list in one place is what lets the Flask backend build a
feature vector in exactly the same order the model was trained on, and
lets tests / the frontend agree on what a "match snapshot" looks like.

We deliberately use the *blue-side* subset of the raw Kaggle columns
(dataset: "League of Legends Diamond Ranked Games (10 min)"), i.e. the
statistics a player can read off their own scoreboard at minute 10. This
keeps the input form on the frontend short while still being a fair,
realistic subset of the real 40-column dataset.
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

# Sensible defaults (roughly the dataset median) so the API/frontend can
# omit fields the user doesn't want to fill in manually.
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
