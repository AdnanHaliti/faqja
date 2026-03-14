# Docker Setup Guide (Recommended for Windows)

## Overview

Docker provides the easiest way to run Nginx with SSL on Windows. This setup uses Docker Compose to orchestrate:
- Nginx reverse proxy (ports 80/443)
- Python backend (internal port 8000)
- Automatic SSL certificate management

## Prerequisites

### Install Docker Desktop for Windows
1. Download: https://www.docker.com/products/docker-desktop
2. Run installer
3. Enable WSL2 integration during setup
4. Restart computer

Verify installation:
```powershell
docker --version
docker-compose --version
```

## Setup Steps

### 1. Obtain SSL Certificate from Let's Encrypt

**Option A: Using WSL2 (Recommended)**
```bash
# In WSL2 Ubuntu terminal:
sudo apt-get update
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone \
  -d www.fieldtechllc.com \
  -d fieldtechllc.com \
  --agree-tos \
  --register-unsupported-tld \
  -m your-email@example.com

# Copy certificates to Windows
# Certificates will be at: /etc/letsencrypt/live/www.fieldtechllc.com/
# Copy to: c:\Users\Ador\Fieldtech\ssl\certs\
```

**Option B: Using Certbot in Docker**
```powershell
# Create SSL directory structure
mkdir ssl\certs, ssl\renewal

# Run Certbot in Docker (requires opening port 80 temporarily)
docker run -it --rm `
  -v "c:\Users\Ador\Fieldtech\ssl\certs:/etc/letsencrypt/live/www.fieldtechllc.com" `
  certbot/certbot certonly --standalone `
  -d www.fieldtechllc.com `
  --agree-tos `
  -m your-email@example.com
```

### 2. Create SSL Directory Structure
```powershell
# In c:\Users\Ador\Fieldtech\
mkdir ssl\certs
mkdir ssl\renewal

# Copy Let's Encrypt certificates:
# Copy: /etc/letsencrypt/live/www.fieldtechllc.com/* 
# To:   c:\Users\Ador\Fieldtech\ssl\certs\
```

Expected files:
```
ssl\certs\
  ├── fullchain.pem
  ├── privkey.pem
  ├── chain.pem
  └── cert.pem
```

### 3. Start Docker Compose

```powershell
cd c:\Users\Ador\Fieldtech

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart
docker-compose restart
```

### 4. Verify Everything Works

```powershell
# Check containers are running
docker-compose ps

# Test HTTP redirect to HTTPS
curl -I http://localhost

# Test HTTPS (ignore cert warning in dev)
curl -k -I https://localhost

# Test from Python backend
Invoke-WebRequest -Uri "https://localhost" -SkipCertificateCheck
```

## Port Blocking (Windows Firewall)

```powershell
# Run as Administrator
# List all inbound rules
Get-NetFirewallRule -Direction Inbound -Enabled True | Select-Object DisplayName

# Create rule to block all inbound except SSH, HTTP, HTTPS
New-NetFirewallRule -DisplayName "BlockAll" -Direction Inbound -Action Block -Enabled True
New-NetFirewallRule -DisplayName "AllowHTTP" -Direction Inbound -Action Allow -LocalPort 80 -Protocol TCP
New-NetFirewallRule -DisplayName "AllowHTTPS" -Direction Inbound -Action Allow -LocalPort 443 -Protocol TCP
New-NetFirewallRule -DisplayName "AllowSSH" -Direction Inbound -Action Allow -LocalPort 22 -Protocol TCP
```

## Certificate Renewal

### Auto-renewal in Docker (Recommended)
Add a renewal service to `docker-compose.yml`:

```yaml
certbot:
  image: certbot/certbot
  container_name: fieldtech-certbot
  volumes:
    - ./ssl/certs:/etc/letsencrypt/live/www.fieldtechllc.com
    - ./ssl/renewal:/etc/letsencrypt
  entrypoint: /bin/sh -c 'trap exit TERM; while :; do certbot renew --quiet; sleep 12h & wait $!; done'
  depends_on:
    - nginx
  networks:
    - fieldtech-network
```

### Manual Renewal
```powershell
# Stop Nginx
docker-compose pause nginx

# Renew certificate
docker run -it --rm `
  -v "c:\Users\Ador\Fieldtech\ssl\certs:/etc/letsencrypt/live/www.fieldtechllc.com" `
  -v "c:\Users\Ador\Fieldtech\ssl\renewal:/etc/letsencrypt" `
  certbot/certbot renew

# Restart Nginx
docker-compose unpause nginx
```

## Monitoring & Logs

```powershell
# View all logs
docker-compose logs

# Follow logs for specific service
docker-compose logs -f nginx
docker-compose logs -f fieldtech-backend

# View Nginx access logs
docker exec fieldtech-nginx cat /var/log/nginx/fieldtech_access.log

# View Nginx error logs
docker exec fieldtech-nginx cat /var/log/nginx/fieldtech_error.log
```

## Troubleshooting

### Nginx won't start
```powershell
# Check logs
docker-compose logs nginx

# Validate nginx config
docker exec fieldtech-nginx nginx -t

# Common issues:
# - Port 80/443 already in use
# - Certificate files not found
# - nginx.conf has syntax errors
```

### Certificate issues
```powershell
# Check certificate expiry
docker exec fieldtech-nginx openssl x509 -in /etc/letsencrypt/live/www.fieldtechllc.com/cert.pem -noout -dates

# Verify certificate files exist
docker exec fieldtech-nginx ls -la /etc/letsencrypt/live/www.fieldtechllc.com/

# Test certificate with curl
curl -v https://localhost --cacert "c:\Users\Ador\Fieldtech\ssl\certs\fullchain.pem"
```

### Backend not responding
```powershell
# Check if Python server is running
docker-compose ps

# View backend logs
docker-compose logs fieldtech-backend

# Test backend directly (through Nginx)
docker exec fieldtech-nginx curl http://fieldtech-backend:8000
```

## Production Deployment

For production, consider:
1. **Use Docker Swarm or Kubernetes** for orchestration
2. **Enable SSL certificate auto-renewal** with certbot sidecar
3. **Set resource limits** in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```
4. **Use environment variables** for configuration
5. **Enable Docker health checks** (already configured)
6. **Backup certificates** regularly
7. **Monitor logs** with ELK stack or similar

## File Structure

```
c:\Users\Ador\Fieldtech\
├── index.html
├── script.js
├── styles.css
├── server.py
├── nginx.conf
├── docker-compose.yml
├── Dockerfile.backend
├── NGINX_SETUP.md
├── DOCKER_SETUP.md (this file)
└── ssl/
    ├── certs/
    │   ├── fullchain.pem
    │   ├── privkey.pem
    │   ├── chain.pem
    │   └── cert.pem
    └── renewal/
```

## Quick Start Summary

```powershell
# 1. Get certificate (WSL2)
# Run in WSL2 Ubuntu and copy certs to ssl\certs\

# 2. Create directories
mkdir ssl\certs, ssl\renewal

# 3. Start services
docker-compose up -d

# 4. Test
curl -k https://localhost

# 5. View logs
docker-compose logs -f
```
