"""Flask application factory serving the LoL win-probability model.

Endpoints
---------
GET  /health   liveness/readiness probe used by CI integration tests, the
               Docker HEALTHCHECK, and the "backend health status" metric.
POST /predict  takes a (partial) 10-minute match snapshot and returns the
               blue-side win probability from the model currently
               deployed in MLFLOW_MODEL_STAGE (Staging or Production).
GET  /metrics  Prometheus scrape endpoint (see app/metrics.py).
"""

from __future__ import annotations

import logging
import time

from flask import Flask, jsonify, request
from flask_cors import CORS

from .config import Config
from .features import FEATURE_COLUMNS, build_feature_vector
from .metrics import (
    APP_UP,
    PREDICT_LATENCY_SECONDS,
    PREDICT_REQUESTS_FAILED_TOTAL,
    PREDICT_REQUESTS_TOTAL,
    metrics_response,
)
from .model_loader import load_model, model_metadata, predict_win_probability

logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=Config.CORS_ORIGINS.split(",") if Config.CORS_ORIGINS != "*" else "*")

    try:
        load_model()
    except RuntimeError as exc:
        logging.warning("%s /predict will fail until one is registered/promoted.", exc)

    @app.get("/health")
    def health():
        APP_UP.set(1)
        return jsonify(status="ok", environment=Config.ENVIRONMENT, **model_metadata())

    @app.post("/predict")
    def predict():
        PREDICT_REQUESTS_TOTAL.inc()
        start = time.perf_counter()
        try:
            payload = request.get_json(silent=True) or {}
            unknown = set(payload) - set(FEATURE_COLUMNS)
            if unknown:
                PREDICT_REQUESTS_FAILED_TOTAL.inc()
                return jsonify(error=f"Unknown feature(s): {sorted(unknown)}"), 400

            feature_vector = build_feature_vector(payload)
            win_probability = predict_win_probability(feature_vector)
            return jsonify(
                blue_win_probability=round(win_probability, 4),
                predicted_winner="blue" if win_probability >= 0.5 else "red",
                **model_metadata(),
            )
        except Exception as exc:  # noqa: BLE001 - convert any failure into a JSON 500
            PREDICT_REQUESTS_FAILED_TOTAL.inc()
            logging.exception("Prediction failed")
            return jsonify(error=str(exc)), 500
        finally:
            PREDICT_LATENCY_SECONDS.observe(time.perf_counter() - start)

    @app.get("/metrics")
    def metrics():
        return metrics_response()

    return app
