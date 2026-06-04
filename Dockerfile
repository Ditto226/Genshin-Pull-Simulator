# Use a slim, lightweight official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for build steps (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file from your host machine into the container
COPY requirements.txt .

# Install the dependencies from the file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local project files into the container's working directory
COPY . /app

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Run the server configuration.
CMD ["python", "Codes/server.py"]