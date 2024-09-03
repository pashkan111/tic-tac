# Use the official Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the poetry files for caching dependencies
COPY poetry.lock pyproject.toml /app/

# Install Poetry
RUN pip install --no-cache-dir poetry

# Configure Poetry to not use virtual environments
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .
