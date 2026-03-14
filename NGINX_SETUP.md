# FieldTech Nginx + SSL Setup Guide

## Overview
This guide sets up Nginx as a reverse proxy in front of the Python server with SSL/TLS encryption via Let's Encrypt.

**Architecture:**
```
Internet (Port 80/443)
    ↓
Nginx (Reverse Proxy)
    ↓
Python Server (localhost:8000)
```

## Prerequisites

### For Linux/macOS:
```bash
# Install Nginx
sudo apt-get install nginx  # Ubuntu/Debian
brew install nginx          # macOS

# Install Certbot for Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx  # Ubuntu/Debian
brew install certbot        # macOS
```

### For Windows:
Note: Windows support is limited. Recommended alternatives:
1. Use Windows Subsystem for Linux (WSL2) + Linux nginx
2. Use IIS with SSL (built-in to Windows)
3. Use Docker + Nginx container

**For WSL2 Ubuntu:**
```powershell
# In PowerShell as Administrator
wsl --install -d Ubuntu
```

Then in WSL2 Ubuntu:
```bash
sudo apt-get update
sudo apt-get install nginx certbot python3-certbot-nginx
```

## Setup Steps (Linux/macOS/WSL2)

### 1. Copy Nginx Configuration
```bash
# For Ubuntu/Debian
sudo cp nginx.conf /etc/nginx/sites-available/fieldtech.conf
sudo ln -s /etc/nginx/sites-available/fieldtech.conf /etc/nginx/sites-enabled/

# For macOS
sudo cp nginx.conf /usr/local/etc/nginx/servers/fieldtech.conf
```

### 2. Obtain SSL Certificate (Let's Encrypt)
```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Get certificate with certbot (standalone mode - no nginx required)
sudo certbot certonly --standalone -d www.fieldtechllc.com -d fieldtechllc.com

# Follow prompts:
# - Enter email for renewal notifications
# - Accept terms
# - Certbot will verify domain ownership and issue cert
```

Certificate files will be created at:
- `/etc/letsencrypt/live/www.fieldtechllc.com/fullchain.pem`
- `/etc/letsencrypt/live/www.fieldtechllc.com/privkey.pem`

### 3. Start Services

**Start Python backend:**
```bash
cd /path/to/FieldTech
python3 server.py
```

**Start Nginx:**
```bash
# Ubuntu/Debian
sudo systemctl start nginx
sudo systemctl enable nginx  # Auto-start on boot

# macOS
sudo brew services start nginx
```

### 4. Verify Setup
```bash
# Test nginx config
sudo nginx -t

# Check if listening on ports 80 and 443
sudo netstat -tulpn | grep nginx

# Test SSL certificate
curl -I https://www.fieldtechllc.com
```

### 5. Auto-Renew SSL Certificates
```bash
# Set up cron job for automatic renewal
sudo certbot renew --dry-run  # Test renewal

# Certbot automatically creates a systemd timer on modern Linux:
sudo systemctl start certbot.timer
sudo systemctl enable certbot.timer

# Or manual monthly cron:
# 0 2 1 * * sudo certbot renew --quiet
```

## Port Blocking (Firewall)

### Ubuntu/Debian (UFW):
```bash
# Reset to defaults
sudo ufw reset

# Allow only 22 (SSH), 80 (HTTP), 443 (HTTPS)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### macOS (pf firewall):
```bash
# Edit /etc/pf.conf to block all ports except 22, 80, 443
sudo nano /etc/pf.conf
```

### Windows Firewall (if running on Windows):
```powershell
# PowerShell (Run as Administrator)
# Block all inbound except 22, 80, 443
New-NetFirewallRule -DisplayName "Block All Ports" -Direction Inbound -Action Block -Enabled True
New-NetFirewallRule -DisplayName "Allow SSH" -Direction Inbound -Action Allow -LocalPort 22 -Protocol TCP
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Action Allow -LocalPort 80 -Protocol TCP
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Action Allow -LocalPort 443 -Protocol TCP
```

## Monitoring & Logs

```bash
# View Nginx error logs
sudo tail -f /var/log/nginx/fieldtech_error.log

# View access logs
sudo tail -f /var/log/nginx/fieldtech_access.log

# Restart Nginx after config changes
sudo systemctl restart nginx
sudo nginx -s reload  # On macOS

# Check Nginx status
sudo systemctl status nginx
```

## Troubleshooting

### Certificate Not Renewing
```bash
# Manual renewal
sudo certbot renew --force-renewal

# Check renewal log
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Nginx Won't Start
```bash
# Test configuration
sudo nginx -t

# Check if ports are in use
sudo lsof -i :80
sudo lsof -i :443

# Kill process using port (if needed)
sudo kill -9 <PID>
```

### Connection Refused
```bash
# Ensure Python backend is running
ps aux | grep server.py

# Check if Python server is listening on 8000
sudo netstat -tulpn | grep 8000
```

## Security Summary

✅ **HTTPS Enforced:** All HTTP traffic redirected to HTTPS
✅ **Port Blocking:** Only ports 80/443 open, all others blocked
✅ **SSL/TLS:** TLS 1.2/1.3 with strong ciphers
✅ **HSTS:** Browser forced to use HTTPS (1 year)
✅ **Security Headers:** CSP, X-Frame-Options, X-Content-Type-Options set
✅ **Rate Limiting:** 10 req/sec per IP with burst protection
✅ **Auto-Renewal:** Let's Encrypt certificates auto-renew before expiry

## Certificate Expiry

Certificates expire after 90 days. Certbot automatically renews them 30 days before expiry.

Check expiry date:
```bash
sudo certbot certificates
```
