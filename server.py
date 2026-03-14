#!/usr/bin/env python3
"""
Custom HTTP server with host restrictions, security headers, IP-based rate limiting,
input sanitization, and XSS/command injection prevention.
Allowed hosts: www.fieldtechllc.com, localhost, 127.0.0.1
Rate limit: 100 requests per minute per IP
"""

import http.server
import socketserver
import os
import time
import re
import html
import urllib.parse
from collections import defaultdict
from pathlib import Path

ALLOWED_HOSTS = ['www.fieldtechllc.com', 'localhost', '127.0.0.1', 'fieldtechllc.com']
PORT = 8000

# Rate limiting config
RATE_LIMIT_REQUESTS = 100  # requests
RATE_LIMIT_WINDOW = 60     # seconds

# Security patterns to detect injection attempts
INJECTION_PATTERNS = [
    r'[;&|`$(){}[\]<>]',           # Shell metacharacters
    r'\.\./',                       # Path traversal
    r'\x00',                        # Null byte
    r'<script|javascript:|onerror|onload|onclick',  # XSS patterns
    r'union\s+select|drop\s+table|delete\s+from',   # SQL injection patterns
]

class InputValidator:
    """Validates and sanitizes user input"""
    
    @staticmethod
    def has_injection_attempt(text, allow_slashes=False):
        """Check if text contains potential injection patterns"""
        if not isinstance(text, str):
            return False
        
        # Check each injection pattern
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_path(path):
        """Sanitize file path to prevent traversal attacks"""
        # Remove null bytes
        path = path.replace('\x00', '')
        
        # Normalize path
        normalized = os.path.normpath(path)
        
        # Prevent directory traversal
        if '..' in normalized or normalized.startswith('/'):
            return None
        
        return normalized
    
    @staticmethod
    def escape_html(text):
        """Escape HTML special characters to prevent XSS"""
        return html.escape(text)

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_requests = defaultdict(list)  # {ip: [timestamp, timestamp, ...]}
        self.ip_violations = defaultdict(int)  # Track suspicious attempts per IP
    
    def is_allowed(self, ip):
        """Check if IP is within rate limit. Returns (allowed, remaining_requests)"""
        now = time.time()
        cutoff_time = now - self.window_seconds
        
        # Remove old timestamps outside the window
        self.ip_requests[ip] = [t for t in self.ip_requests[ip] if t > cutoff_time]
        
        current_count = len(self.ip_requests[ip])
        
        if current_count >= self.max_requests:
            return False, 0
        
        # Record this request
        self.ip_requests[ip].append(now)
        
        remaining = self.max_requests - current_count - 1
        return True, remaining
    
    def record_violation(self, ip):
        """Record a security violation attempt from an IP"""
        self.ip_violations[ip] += 1

rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)
validator = InputValidator()

class RestrictedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        host = self.headers.get('Host', '').split(':')[0]
        
        # Parse and validate path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = parsed_path.query
        
        # Check for injection attempts in path and query
        if validator.has_injection_attempt(path) or validator.has_injection_attempt(query):
            rate_limiter.record_violation(client_ip)
            self.send_error(400, 'Invalid request: Suspicious characters detected')
            self.log_message('SECURITY: Injection attempt detected in GET request from %s', client_ip)
            return
        
        # Validate path doesn't escape allowed directory
        sanitized_path = validator.sanitize_path(path.lstrip('/'))
        if sanitized_path is None:
            rate_limiter.record_violation(client_ip)
            self.send_error(400, 'Invalid request: Path traversal detected')
            self.log_message('SECURITY: Path traversal attempt from %s', client_ip)
            return
        
        # Check rate limit
        allowed, remaining = rate_limiter.is_allowed(client_ip)
        if not allowed:
            self.send_error(429, f'Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds')
            return
        
        # Check if host is in allowed list
        if host not in ALLOWED_HOSTS:
            rate_limiter.record_violation(client_ip)
            self.send_error(403, f'Host not allowed')
            self.log_message('SECURITY: Host validation failed from %s (Host: %s)', client_ip, validator.escape_html(host))
            return
        
        # Call parent's do_GET with validated path
        super().do_GET()
    
    def do_POST(self):
        client_ip = self.client_address[0]
        host = self.headers.get('Host', '').split(':')[0]
        
        # Parse request path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Check for injection attempts in path
        if validator.has_injection_attempt(path):
            rate_limiter.record_violation(client_ip)
            self.send_error(400, 'Invalid request: Suspicious characters detected')
            self.log_message('SECURITY: Injection attempt in POST from %s', client_ip)
            return
        
        # Validate path doesn't escape allowed directory
        sanitized_path = validator.sanitize_path(path.lstrip('/'))
        if sanitized_path is None:
            rate_limiter.record_violation(client_ip)
            self.send_error(400, 'Invalid request: Path traversal detected')
            self.log_message('SECURITY: Path traversal in POST from %s', client_ip)
            return
        
        # Check rate limit
        allowed, remaining = rate_limiter.is_allowed(client_ip)
        if not allowed:
            self.send_error(429, f'Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds')
            return
        
        # Check if host is in allowed list
        if host not in ALLOWED_HOSTS:
            rate_limiter.record_violation(client_ip)
            self.send_error(403, f'Host not allowed')
            self.log_message('SECURITY: Host validation failed in POST from %s', client_ip)
            return
        
        # Call parent's do_POST
        super().do_POST()
    
    def end_headers(self):
        # Add security headers for XSS prevention
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;")
        super().end_headers()
    
    def log_message(self, format, *args):
        # Enhanced logging with IP and escaping
        client_ip = self.client_address[0]
        # Escape any user input in logs
        escaped_args = tuple(
            validator.escape_html(str(arg)) if isinstance(arg, str) else arg 
            for arg in args
        )
        print(f'[{self.log_date_time_string()}] [{client_ip}] {format % escaped_args}')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(('', PORT), RestrictedHTTPRequestHandler) as httpd:
        print(f'Server running at http://localhost:{PORT}')
        print(f'Allowed hosts: {", ".join(ALLOWED_HOSTS)}')
        print(f'Rate limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds per IP')
        print('Security: Input validation, XSS prevention, Command injection prevention')
        print('Press Ctrl+C to stop...')
        httpd.serve_forever()
