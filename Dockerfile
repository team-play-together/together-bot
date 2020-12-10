FROM python:3.8.6
LABEL maintainer="StaySharp0@gmail.com"

# Install poetry
RUN wget https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py &&\
    python get-poetry.py --preview --yes &&\
    rm -f get-poetry.py
ENV PATH="/root/.poetry/bin:${PATH}"
RUN poetry config virtualenvs.create false

# Install dependencies
WORKDIR /app
COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry install

ENTRYPOINT ["poetry", "run", "bot"]