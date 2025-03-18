FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="${PYTHONPATH}:/bot"

RUN pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_CREATE=false 

WORKDIR /bot

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . /bot
