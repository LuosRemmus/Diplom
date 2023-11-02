FROM python:3.10-slim AS development

ARG POETRY_HOME=/etc/poetry
RUN apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y libyaml-dev curl && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python - --version 1.4.0 && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="${PATH}:${POETRY_HOME}/bin"

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache && \
    rm -rf ~/.cache ~/.config/pypoetry/auth.toml

COPY alembic.ini /alembic.ini
COPY /src /src

ENV PYTHONPATH="/"
CMD ["python3", "backend/main.py"]

FROM development as production
RUN poetry install --without dev --sync --no-cache
CMD ["python3", "backend/main.py"]