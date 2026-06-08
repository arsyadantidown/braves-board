#!/bin/sh
set -e

MAX_RETRIES=30
RETRY_INTERVAL=2
retries=0

echo "Waiting for database..."

until python -c "
import socket, sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect(('db', 5432))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    retries=$((retries + 1))
    if [ "$retries" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: Database tidak ready setelah ${MAX_RETRIES} percobaan. Abort."
        exit 1
    fi
    printf "  database belum siap, mencoba lagi dalam %ss... (%s/%s)\n" \
        "$RETRY_INTERVAL" "$retries" "$MAX_RETRIES"
    sleep "$RETRY_INTERVAL"
done

echo "Database ready!"

if [ -n "${TRUSTED_PROXY_IPS}" ]; then
    TRUSTED_IPS="${TRUSTED_PROXY_IPS}"
    echo "INFO: Menggunakan TRUSTED_PROXY_IPS dari environment: ${TRUSTED_IPS}"
else
    NGINX_IP=$(python -c "
import socket
try:
    print(socket.gethostbyname('nginx'))
except Exception:
    pass
" 2>/dev/null)

    if [ -n "${NGINX_IP}" ]; then
        TRUSTED_IPS="${NGINX_IP}"
        echo "INFO: Auto-detected IP nginx container: ${TRUSTED_IPS}"
    else
        TRUSTED_IPS="127.0.0.1"
        echo "WARNING: TRUSTED_PROXY_IPS tidak di-set dan service 'nginx' tidak ditemukan."
        echo "         Fallback ke 127.0.0.1"
    fi
fi

echo "Starting API... (trusted proxy: ${TRUSTED_IPS})"

exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --forwarded-allow-ips="${TRUSTED_IPS}"