FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY wsgi.py .

ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}
ENV PORT=5000
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",5000)}/health')" || exit 1

# Single worker + threads: prometheus_client counters live in process memory,
# so multiple workers would each keep their own copy and Prometheus would
# scrape a different (partial) count each time, making "total prediction
# requests" wrong on the dashboard. One threaded worker keeps the metrics
# correct and is ample for this app's load. Scale out with prometheus
# multiprocess mode if you ever need more workers.
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "wsgi:app"]
