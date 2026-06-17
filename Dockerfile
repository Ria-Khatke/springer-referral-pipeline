# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first (better layer caching)
COPY requirements.txt .

# Upgrade pip first, then install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Run both scripts when the container starts
CMD ["sh", "-c", "python profiling.py && python pipeline.py"]