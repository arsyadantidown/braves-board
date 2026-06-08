set -e

# Nginx Entrypoint
# - Generate self-signed SSL cert for development
# - Start Nginx

CERT_DIR="/etc/nginx/ssl"
CERT_FILE="${CERT_DIR}/server.crt"
KEY_FILE="${CERT_DIR}/server.key"

if [ ! -f "${CERT_FILE}" ] || [ ! -f "${KEY_FILE}" ]; then
    echo "Generating self-signed SSL certificate..."
    
    openssl req -x509 \
        -nodes \
        -days 365 \
        -newkey rsa:2048 \
        -keyout "${KEY_FILE}" \
        -out "${CERT_FILE}" \
        -subj "/C=ID/ST=Jakarta/L=Jakarta/O=BravesBoard/OU=Development/CN=localhost"
    
    chmod 600 "${KEY_FILE}"
    chmod 644 "${CERT_FILE}"
    
    echo "SSL certificate generated successfully."
else
    echo "SSL certificate already exists, skipping generation."
fi

echo "Starting Nginx..."

exec nginx -g "daemon off;"