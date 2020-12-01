FROM python:3.8.6
LABEL maintainer="StaySharp0@gmail.com"
WORKDIR /usr/src/app/together-bot

RUN \
# change apt refo
  sed -i -e 's/http:\/\/deb.debian.org\/debian/http:\/\/mirror.kakao.com\/debian/g' /etc/apt/sources.list; \
  apt-get update; \
  apt-get -y install locales; \
 # generate ko_KR.UTF-8
  locale-gen ko_KR.UTF-8

RUN \
  # clone project
  git clone https://github.com/team-play-together/together-bot.git && \
  # install poetry
  cd together-bot; \
  pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install

ENTRYPOINT ["bash"]