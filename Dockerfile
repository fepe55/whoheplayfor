FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

ARG DEV_MODE=0

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    sh -c "if [ \"$DEV_MODE\" -eq 1 ]; then uv sync --frozen --no-install-project; else uv sync --frozen --no-install-project --no-dev; fi"

ADD . /app

RUN set -ex \
    && apk add --no-cache bash \
    && uv run python manage.py collectstatic --no-input

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

EXPOSE 8000

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "whoheplayfor.wsgi"]
