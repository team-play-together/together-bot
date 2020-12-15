FROM python:3.8.6

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin:${PATH}"
RUN poetry config virtualenvs.create false

# Install dependencies
WORKDIR /app
COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry install --no-dev -n

COPY logging.yml /app/
COPY together_bot/ /app/together_bot/

ENTRYPOINT ["poetry", "run", "bot"]
