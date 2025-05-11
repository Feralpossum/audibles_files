# Use the official slim Python 3.12 image
FROM python:3.12-slim

# Install system ffmpeg (optional) and clean up apt cache
RUN apt update && \
    apt install -y ffmpeg && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your application code (including your static ffmpeg binary)
COPY . .

# Make sure your static ffmpeg binary is executable
RUN chmod +x /app/ffmpeg

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Diagnostic startup + run your bot
CMD echo "✅ Container started; showing contents..." && \
    ls -la /app && \
    echo "📦 Attempting to run main.py..." && \
    python -u main.py
