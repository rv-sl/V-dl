FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt update && apt install -y ffmpeg && \
    pip install --no-cache-dir -r requirements.txt

#CMD gunicorn --bind 0.0.0.0:8000 app:app & python3 bot.py
CMD ["python3", "start.py"]
