# Use a specific version of Python
FROM python:3.9.9-slim-buster

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install build dependencies and Chrome dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    wget \
    curl \
    unzip \
    libx11-6 \
    libglib2.0-0 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxi6 \
    libxtst6 \
    libpangocairo-1.0-0 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libatk-bridge2.0-0 \
    libgbm1 \
    libgtk-3-0 \
    libdrm2 \
    fonts-liberation \
    libappindicator3-1 \
    libjpeg-dev \
    libgconf-2-4 \
    chromium \
    chromium-driver

# Add a command to print Chromium version for verification
RUN chromium --version

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 5000

# Set the entrypoint command
CMD ["python", "main.py"]
