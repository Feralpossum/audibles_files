FROM python:3.12-slim

RUN apt update && \
    apt install -y ffmpeg && \
    apt clean

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Diagnostic steps before starting your bot
CMD echo "✅ Container started; showing contents..." && \
    ls -la && \
    echo "📦 Attempting to run main.py..." && \
    python -u main.py
