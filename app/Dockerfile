FROM python:3.10-slim-bookworm

# Environment settings for cleaner, safer behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install system deps temporarily for build, then remove to reduce vulnerabilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y build-essential \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# Now copy the full project
COPY . .

# Run the app
CMD ["python", "main.py"]
