"""Integration test #2: POST /predict, end to end through the real registered model.

Exercises the full request path (Flask route -> feature vector -> MLflow
model -> JSON response) against the model trained and promoted by the
`trained_registry_uri` fixture, so it would fail if the API contract, the
feature ordering, or the model-loading code ever drifted apart.
"""


def test_predict_returns_a_probability_and_traceability_fields(client):
    response = client.post("/predict", json={"blueGoldDiff": 1500, "blueKills": 8, "blueDeaths": 3})

    assert response.status_code == 200
    body = response.get_json()
    assert 0.0 <= body["blue_win_probability"] <= 1.0
    assert body["predicted_winner"] in {"blue", "red"}
    assert body["model_stage"] == "Production"


def test_predict_favors_blue_when_blue_has_a_massive_lead(client):
    response = client.post(
        "/predict",
        json={
            "blueGoldDiff": 8000,
            "blueExperienceDiff": 6000,
            "blueKills": 15,
            "blueDeaths": 1,
            "blueDragons": 2,
            "blueHeralds": 1,
            "blueTowersDestroyed": 2,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["predicted_winner"] == "blue"


def test_predict_rejects_unknown_feature_names(client):
    response = client.post("/predict", json={"thisIsNotAFeature": 1})

    assert response.status_code == 400
    assert "thisIsNotAFeature" in response.get_json()["error"]
