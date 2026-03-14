#!/bin/bash

# Deployment script for FieldTech website
# Run this script in the /opt/docker/data/web/ directory on your remote machine

echo "Deploying FieldTech website..."

# Build and start the container
docker-compose up -d --build

# Check if the container is running
if [ $? -eq 0 ]; then
    echo "Deployment successful!"
    echo "Container 'fieldtech-website' is now running."
    echo ""
    echo "Next steps:"
    echo "1. Configure Nginx Proxy Manager to route traffic to this container"
    echo "2. Set up SSL certificate through Nginx Proxy Manager"
    echo ""
    echo "To check container status: docker ps | grep fieldtech-website"
    echo "To view logs: docker logs -f fieldtech-website"
else
    echo "Deployment failed!"
    exit 1
fi