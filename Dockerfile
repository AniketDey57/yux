FROM python:slim

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg gcc

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app


CMD [ "python3", "/app/bot.py"]
