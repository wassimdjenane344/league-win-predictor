"""GET /health against a real Flask app + real MLflow registry."""


def test_health_endpoint_reports_ok_and_model_metadata(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["model_name"] == "lol-win-predictor"
    assert body["model_stage"] == "Production"
    assert body["model_version"] is not None
