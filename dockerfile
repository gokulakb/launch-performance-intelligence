# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install setuptools==69.0.3 && \
    pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Initialize the database during build
RUN python render_init.py

# Expose the Streamlit port
EXPOSE 10000

# Set environment variables
ENV RENDER=true
ENV PYTHONUNBUFFERED=1

# Run the application
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false --server.maxUploadSize=10
