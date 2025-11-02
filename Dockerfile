# Use the official slim Python 3.12 base image
FROM python:3.12-slim

# 1) Install ffmpeg + libopus (Discord voice depends on Opus)
# 2) Keep image small (no recommends, clean apt cache)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libopus0 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Make Python output unbuffered (cleaner logs)
ENV PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# Copy app code
COPY . .

# If you previously committed a static ffmpeg, make sure it isn't used
RUN rm -f /app/ffmpeg

# Install Python deps
# (ideally pin: discord.py[voice]==2.4.0, aiohttp>=3.9.5, PyNaCl>=1.5.0, requests>=2.32.0)
RUN pip install --no-cache-dir -r requirements.txt

# Optional: quick sanity check (won’t fail build if missing)
# RUN ffmpeg -version || true

# Run the bot
CMD ["python", "-u", "main.py"]
