FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ACEest_Fitness.py .
COPY aceest_fitness/ ./aceest_fitness/

FROM base AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests/ ./tests/
CMD ["python", "-m", "pytest", "-q", "tests"]

FROM base AS runtime
ARG APP_VERSION=3.2.4-web
ENV APP_VERSION=${APP_VERSION}
RUN groupadd --system app && useradd --system --gid app --home-dir /app app && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=3)" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--access-logfile", "-", "ACEest_Fitness:app"]
