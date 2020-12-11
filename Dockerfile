FROM python:3.8.6
LABEL maintainer="StaySharp0@gmail.com"

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - &&\
    rm -f get-poetry.py
ENV PATH="/root/.poetry/bin:${PATH}"
RUN poetry config virtualenvs.create false

# Install dependencies
WORKDIR /app
COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry install

ENTRYPOINT ["poetry", "run", "bot"]