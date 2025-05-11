# Use the official slim Python 3.12 base image
FROM python:3.12-slim

# Install system ffmpeg and clean up apt caches
RUN apt update && \
    apt install -y ffmpeg && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory in the container
WORKDIR /app

# Copy your application code into the container
COPY . .

# Remove any bundled static ffmpeg binary so your code uses the distro’s ffmpeg
RUN rm -f /app/ffmpeg

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "-u", "main.py"]
