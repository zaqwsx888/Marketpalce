FROM python:3.9

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app

COPY ./djangoProject /app


