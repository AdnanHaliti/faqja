# Docker Setup Guide

## Quick Start (Standalone)

For a quick local deployment, use the default docker-compose.yml which exposes port 8000:

```bash
docker compose up -d
```

The website will be accessible at `http://localhost:8000`.

## Production Setup (With Nginx Proxy Manager)

For production deployments with SSL and domain routing, use the production configuration:

1. Make sure you have Nginx Proxy Manager running with the network `nginxproxymanager_default`
2. Update the docker-compose.yml to use the external network (see docker-compose.prod.yml for reference)
3. Run the container:

```bash
docker compose -f docker-compose.prod.yml up -d
```

4. Configure a proxy host in Nginx Proxy Manager pointing to `fieldtech-website:8000`

## Troubleshooting

### Common Issues:

1. **Network Error**: If you get a "network not found" error, make sure the `nginxproxymanager_default` network exists or use the standalone configuration.

2. **Build Errors**: If Docker build fails, ensure all required directories (`assets`, `logo`) exist in the project root.

3. **Permission Issues**: The Dockerfile handles file permissions for the assets and logo directories automatically.

### Rebuilding:

If you need to rebuild the image after changes:

```bash
docker compose build --no-cache
docker compose up -d
```

## Security Features

The Python server includes:
- Host restrictions (only allows specific domains)
- Rate limiting (100 requests per minute per IP)
- XSS protection
- Input sanitization
- Command injection prevention
- Security headers