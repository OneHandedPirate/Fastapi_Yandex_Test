FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

RUN apk add --no-cache file

COPY ./pyproject.toml pyproject.toml

RUN uv sync

COPY . .

ENTRYPOINT ["echo", "Hello, World!"]