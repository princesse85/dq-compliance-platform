# Build stage
FROM python:3.11-bullseye AS builder

# Install build tools
RUN apt-get update && apt-get install -y gcc

# Install dependencies
COPY requirements.in .
RUN pip install --no-cache-dir -r requirements.in

# Runtime stage
FROM python:3.11-slim-bullseye

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy application code
COPY app/ /var/task/app/
COPY models/ /var/task/models/

# Set the CMD to your handler
CMD [ "app.handler.handler" ]