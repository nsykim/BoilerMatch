FROM python:3.11-slim

# Add build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r reqs.txt

EXPOSE 3020
CMD ["python", "src/api.py", "--host=0.0.0.0"]
