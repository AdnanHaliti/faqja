# Minimal Dockerfile for Python server serving index-new.html
FROM python:3.11-slim

WORKDIR /app

# Copy the essential files
COPY server.py .
COPY index-new.html index.html

# Copy assets and logo directories
COPY assets ./assets
COPY logo ./logo

# Set proper ownership for the copied directories
RUN chown -R root:root assets/ 2>/dev/null || true
RUN chown -R root:root logo/ 2>/dev/null || true

# Expose port 8000
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]