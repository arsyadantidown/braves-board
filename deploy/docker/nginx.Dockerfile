# =============================================================================
# Nginx Dockerfile
# - TLS Termination
# - Reverse Proxy to FastAPI
# =============================================================================

FROM nginx:1.27-alpine

# Install openssl for self-signed cert generation
RUN apk add --no-cache openssl

# Create directories
RUN mkdir -p /etc/nginx/ssl /var/www/certbot

# Copy configuration
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf
COPY deploy/nginx/conf.d/ /etc/nginx/conf.d/

# Copy entrypoint
COPY deploy/docker/entrypoints/nginx.sh /entrypoints/nginx.sh
RUN chmod +x /entrypoints/nginx.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoints/nginx.sh"]