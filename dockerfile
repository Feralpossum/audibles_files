# Use official lightweight Python base image
FROM python:3.12-slim

# Install FFmpeg and system dependencies
RUN apt update && \
    apt install -y ffmpeg && \
    apt clean

# Set working directory
WORKDIR /app

# Copy your project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python", "main.py"]
