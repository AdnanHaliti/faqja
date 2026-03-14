# FieldTech Website - Docker Deployment

This is a minimal Docker setup for running the FieldTech website with a Python server, integrated with Nginx Proxy Manager for SSL.

## Deployment on Remote Machine

### 1. Prepare your files
Copy these files to your remote machine in the web directory:
- Dockerfile
- docker-compose.yml
- server.py
- index-new.html
- assets/ (folder)
- logo/ (folder)

### 2. Build and run the container
```bash
# Navigate to the web directory
cd /opt/docker/data/web/

# Build and start the container
docker-compose up -d --build
```

### 3. Configure Nginx Proxy Manager
1. Access your Nginx Proxy Manager at https://your-domain.com:81
2. Click "Proxy Hosts" > "Add Proxy Host"
3. Configure as follows:
   - Domain Names: your-domain.com (replace with your actual domain)
   - Scheme: http
   - Forward Hostname/IP: fieldtech-website
   - Forward Port: 8000
   - Enable "Websockets Support" and "Block Common Exploits"
   - SSL: Enabled
   - SSL Certificate: Select your certificate or request a new Let's Encrypt certificate

### 4. Verify deployment
After configuration, your site will be accessible at https://your-domain.com

## Notes
- The container connects to the nginxproxymanager_default network to communicate with the proxy
- The Python server serves index-new.html as the main landing page
- Assets and logo folders are included for proper site functionality
- Security features are implemented in the Python server (rate limiting, XSS protection, etc.)