FROM python:3.10

RUN mkdir /app
WORKDIR /app

# Turn off buffering in case of crashing
ENV PYTHONUNBUFFERED 1

# Pip Install Dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Staging Files
COPY . /app

CMD ["python", "main.py"]