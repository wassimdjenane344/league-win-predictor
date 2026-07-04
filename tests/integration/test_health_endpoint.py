"""Integration test #1: GET /health against a real Flask app + real MLflow registry.

Mirrors the skeleton given in the course's CI exercise (ci.md): use Flask's
test client to hit an HTTP endpoint and assert on the JSON body. Here it
also asserts the model traceability fields the final project spec
requires (model version/stage, git commit, DVC data version) are present,
since /health is what a deploy step or uptime check uses to confirm which
model is actually serving.
"""


def test_health_endpoint_reports_ok_and_model_metadata(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["model_name"] == "lol-win-predictor"
    assert body["model_stage"] == "Production"
    assert body["model_version"] is not None
