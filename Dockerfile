# Minimal Dockerfile for Python server serving index-new.html
FROM python:3.11-slim

WORKDIR /app

# Copy the essential files
COPY server.py .
COPY index-new.html index.html

# Copy assets and logo directories if they exist
COPY --chown=root:root assets ./assets 2>/dev/null || true
COPY --chown=root:root logo ./logo 2>/dev/null || true

# Expose port 8000
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]