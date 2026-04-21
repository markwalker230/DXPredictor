# Use an official lightweight Python runtime
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (required for pandas/numpy building)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
# We do this before copying code to cache the pip install layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ /app/src/

# Expose Streamlit's default port
EXPOSE 8501

# Add a healthcheck to ensure the container is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Define the command to run the application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
