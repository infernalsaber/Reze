FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .
RUN mkdir downloads
RUN apt-get update && apt-get install -y ffmpeg

CMD ["python3", "-OO", "bot.py"]