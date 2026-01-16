FROM python:3.10-slim

# Set an environment variable for unbuffered Python output
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /src

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev libffi-dev \
    procps wireless-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements and source code into the container
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY . .

# Set the entry point
CMD ["python3", "main.py"]

