"""Prometheus instrumentation.

Counter/Gauge/Histogram objects are created at import time, incremented in
the route handlers, and served through a plain Flask route (rather than the
client's own HTTP server) so the app keeps a single port.
"""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, Info, generate_latest

from .config import Config

APP_INFO = Info("app_info", "Application build information")
APP_INFO.info(
    {
        "version": Config.APP_VERSION,
        "git_commit": Config.GIT_COMMIT,
        "environment": Config.ENVIRONMENT,
    }
)

APP_UP = Gauge("app_up", "1 if the backend is up and able to serve requests")
APP_UP.set(1)

PREDICT_REQUESTS_TOTAL = Counter(
    "predict_requests_total", "Total number of /predict requests received"
)
PREDICT_REQUESTS_FAILED_TOTAL = Counter(
    "predict_requests_failed_total", "Total number of /predict requests that errored"
)
PREDICT_LATENCY_SECONDS = Histogram(
    "predict_request_latency_seconds", "Time spent serving a /predict request"
)


def metrics_response():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
