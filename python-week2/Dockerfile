FROM python:3.14.7-trixie AS builder

WORKDIR /app

ENV PATH="/venv/bin:$PATH"
RUN pip install uv

ADD pyproject.toml .
ADD uv.lock .

RUN uv sync --frozen --no-dev --no-install-project


FROM python:3.14.7-slim-trixie AS runner

WORKDIR /app

RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin app \
    && chown app:app /app

COPY --chown=app:app src /app/src
COPY --chown=app:app alembic.ini /app/alembic.ini
COPY --chown=app:app alembic /app/alembic
COPY --chown=app:app --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

USER app

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn python_week2.main:app --host 0.0.0.0 --port 8000"]