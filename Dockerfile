# Use the official slim Python 3.12 base image
FROM python:3.12-slim

# Install ffmpeg, libopus, libsodium (needed for Discord voice)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ffmpeg \
        libopus0 \
        libsodium23 \
        ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Make sure no local ffmpeg binary conflicts
RUN rm -f /app/ffmpeg

# Install Python dependencies
RUN pip install --no-cache-dir \
    "discord.py[voice]==2.4.0" \
    "PyNaCl>=1.5.0" \
    "aiohttp>=3.9.5"

# Run the bot
CMD ["python", "-u", "main.py"]
