# Discord bot

## Requirement

- [poetry](https://github.com/python-poetry/poetry)

## Run

```sh
poetry install
poetry run bot
```

## Docker
```sh
docker build --tag bot:0.0.0 .
docker run --rm -i -t --mount type=bind,source="$(pwd)",destination=/app bot:0.0.0
```

## Bot permissions

- Manage Role
- Send messages
- Manage messages
- Read message history
- Add reactions
- View Channel

```text
268512320
```

