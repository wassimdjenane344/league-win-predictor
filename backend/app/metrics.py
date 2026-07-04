"""Prometheus instrumentation.

Implements the "Required Metrics" list from the final project spec:
  - total number of prediction requests      -> PREDICT_REQUESTS_TOTAL
  - prediction request latency                -> PREDICT_LATENCY_SECONDS
  - number of failed requests                  -> PREDICT_REQUESTS_FAILED_TOTAL
  - backend uptime / health status             -> APP_UP

Follows the same prometheus_client pattern taught in the course
("Monitoring with prometheus.pdf"): Counter/Info objects created at
import time, incremented inside the route handlers, and served through a
plain Flask route rather than the client's own http server so the app
keeps a single port (12-factor: one process listens on $PORT).
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
