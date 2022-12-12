FROM python:3.10-alpine

WORKDIR /app

# Turn off buffering in case of crashing
ENV PYTHONUNBUFFERED 1

# Install dependencies into container
COPY requirements.txt .
RUN pip install -r requirements.txt

# Staging Files
COPY . .