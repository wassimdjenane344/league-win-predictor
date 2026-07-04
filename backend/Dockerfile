FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY wsgi.py .

ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}
# PORT defaults to 5000 locally but is overridden by the platform (Render,
# Railway, ...) which assigns its own port and expects the app to bind to it.
ENV PORT=5000
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
    CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",5000)}/health')" || exit 1

# Shell form so ${PORT} is expanded at runtime -> binds to whatever port the
# host platform assigns. Single threaded worker keeps the prometheus_client
# counters correct (they live in process memory; multiple workers would each
# keep their own copy and Prometheus would scrape a different partial count).
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-5000} --workers 1 --threads 8 --timeout 120 wsgi:app"]
