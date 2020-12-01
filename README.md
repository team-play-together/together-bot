# Discord bot

## Requirement

- [poetry](https://github.com/python-poetry/poetry)

## Run

```sh
poetry install
poetry run bot
```

## Docker 
### Build image command
docker build --tag bot:0.0.0 .
### Run command
docker run --rm -i -t --mount type=bind,source="$(pwd)",destination=/usr/src/app/together-bot bot:0.0.0
