FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create data directory
RUN mkdir -p data

# Non-root user
RUN useradd -m breathe && chown -R breathe:breathe /app
USER breathe

# Health check
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "import json; print(json.dumps({'status': 'healthy'}))"

ENTRYPOINT ["python", "main.py"]
CMD ["--mode", "treasury"]
