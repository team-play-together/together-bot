# Discord bot

## Requirement

- [poetry](https://github.com/python-poetry/poetry)

## Configuration

```console
# create .venv in workspace
poetry config virtualenvs.in-project true
```

## Run

```sh
poetry install
poetry run bot
```

## Docker

```sh
docker build --tag bot .

# Run Bot with .env file
docker run --env-file .env -it --rm bot
# Or run with `--env`
docker run -e DISCORD_BOT_TOKEN=<BOT_TOKEN> -it --rm bot

# For development
docker run --rm -it --mount type=bind,source="$(pwd)",destination=/app --env-file .env bot bash
```

### Using Docker Compose

```sh
# Run Bot with .env file
docker-compose run --rm bot
# Or run with `--env`
docker-compose run -e DISCORD_BOT_TOKEN=<BOT_TOKEN> --rm bot

# For development
docker-compose -f docker-compose.dev.yml run bot bash
```

## Bot permissions

- Manage Role
- Send messages
- Read message history
- Add reactions
- View Channel

```text
268512320
```
