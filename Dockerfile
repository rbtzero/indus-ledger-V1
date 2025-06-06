FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /indus-ledger

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set Python path
ENV PYTHONPATH=/indus-ledger/src

# Create non-root user
RUN useradd -m -u 1000 indus && chown -R indus:indus /indus-ledger
USER indus

# Default command
CMD ["python", "-m", "pytest", "tests/", "-v"]

# Labels for metadata
LABEL org.opencontainers.image.title="Indus Valley Script Decipherment"
LABEL org.opencontainers.image.description="Complete computational analysis of 2,512 Indus Valley inscriptions"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/rbtzero/indus-ledger-v1" 