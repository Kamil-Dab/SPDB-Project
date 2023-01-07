FROM python:3.10.8-slim

RUN apt-get update

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /app

WORKDIR /app
