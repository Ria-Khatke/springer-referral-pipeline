FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .

# Upgrading pip first -- then installing dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY . .

# Runs both scripts when the container starts
CMD ["sh", "-c", "python profiling.py && python pipeline.py"]