# FieldTech Website - Project Overview

## Project Description
FieldTech is an enterprise IT solutions website that provides comprehensive on-premise, workplace, and IT life-cycle services for businesses of all sizes. The project consists of a modern, responsive website built with HTML, CSS (Tailwind), and JavaScript, served by a secure Python HTTP server with robust security features.

## Architecture
The project uses a microservices architecture with:
- **Frontend**: HTML/CSS/JS with Tailwind CSS framework and Font Awesome icons
- **Backend**: Custom Python HTTP server with security features (rate limiting, input validation, XSS protection)
- **Reverse Proxy**: Nginx for SSL termination and load balancing
- **Containerization**: Docker and Docker Compose for deployment
- **SSL**: Let's Encrypt certificates for HTTPS

## Key Features
- Responsive design with mobile-first approach
- 24/7 remote support and on-site assistance
- Security-focused implementation with XSS protection, rate limiting, and input validation
- WhatsApp integration for customer support
- Contact form with urgency levels
- Modern UI with gradient backgrounds and glass card effects

## File Structure
```
├── deploy.sh                 # Deployment script
├── DOCKER_SETUP.md           # Docker setup guide
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Main Dockerfile
├── Dockerfile.backend       # Backend Dockerfile
├── index-new.html           # Main HTML template
├── index.html               # Served HTML file (copied from index-new.html)
├── NGINX_SETUP.md           # Nginx setup guide
├── nginx.conf               # Nginx configuration
├── README.md                # Main project documentation
├── script.js                # Client-side JavaScript
├── server.py                # Python HTTP server with security features
├── styles.css               # Custom CSS styles
├── template.html            # HTML template
├── .git/                    # Git repository
├── .vscode/                 # VS Code settings
├── assets/                  # Static assets
└── logo/                    # Logo files
```

## Building and Running

### Local Development
1. **Run the Python server directly:**
   ```bash
   python3 server.py
   ```
   The server will start on `http://localhost:8000`

2. **Access the website:**
   - Visit `http://localhost:8000` for local development
   - The server enforces allowed hosts: `www.fieldtechllc.com`, `localhost`, `127.0.0.1`, `fieldtechllc.com`

### Docker Deployment
1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

2. **Deploy script:**
   ```bash
   ./deploy.sh
   ```

### Production Deployment
1. **Configure Nginx Proxy Manager:**
   - Domain Names: your-domain.com
   - Scheme: http
   - Forward Hostname/IP: fieldtech-website
   - Forward Port: 8000
   - Enable SSL with Let's Encrypt certificate

2. **Connect to nginxproxymanager_default network** for communication with the proxy

## Security Features
- **Rate Limiting**: 100 requests per minute per IP address
- **Input Validation**: Sanitizes user input to prevent XSS and command injection
- **Host Restrictions**: Only allows specific domains
- **Security Headers**: Includes X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP, etc.
- **Path Traversal Protection**: Prevents directory traversal attacks
- **Injection Prevention**: Detects and blocks potential injection attempts

## Development Conventions
- HTML follows semantic structure with proper accessibility attributes
- CSS uses Tailwind classes with custom overrides in styles.css
- JavaScript implements scroll animations, form handling, and WhatsApp rate limiting
- Python server follows security best practices with input validation and rate limiting
- All external resources are properly referenced with security policies

## Environment Configuration
- **Port**: 8000 (internal), 80/443 (external via Nginx)
- **Allowed Hosts**: www.fieldtechllc.com, localhost, 127.0.0.1, fieldtechllc.com
- **Rate Limit**: 100 requests per minute per IP
- **Security Policies**: Strict Content Security Policy, HSTS, and other security headers

## Deployment Notes
- The container connects to the nginxproxymanager_default network to communicate with the proxy
- The Python server serves index-new.html as the main landing page (renamed to index.html in Docker)
- Assets and logo folders are included for proper site functionality
- Security features are implemented in the Python server (rate limiting, XSS protection, etc.)