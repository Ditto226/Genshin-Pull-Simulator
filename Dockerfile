# Use a slim, lightweight official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for build steps (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install the exact Python packages your code explicitly imports
# This saves you from needing a requirements.txt file right now!
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.28.0 \
    pydantic==2.6.4 \
    requests==2.31.0

# Copy the local project files into the container's working directory
COPY . /app

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Run the server configuration. We override the host to 0.0.0.0 
# so it can accept requests coming from outside the Docker container container.
CMD ["python", "Codes/server.py"]