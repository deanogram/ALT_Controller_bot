FROM python:3.11-slim AS base

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install .

CMD ["uvicorn", "alt_controller_bot.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
