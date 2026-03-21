# --- Stage 1: Build the Go performance component ---
FROM golang:1.24-alpine AS go-builder
WORKDIR /build
COPY workers/golang/go.mod workers/golang/go.sum ./
RUN go mod download
COPY workers/golang/main.go .
RUN go build -o orderbook-worker-go main.go

# --- Stage 2: Final runtime image ---
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy the Go binary from the builder stage
COPY --from=go-builder /build/orderbook-worker-go /app/orderbook-worker-go

# Default command
CMD ["python", "api/app.py"]
