FROM python:3.12-slim

RUN apt update && \
    apt install -y ffmpeg && \
    apt clean

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "main.py"]
