
# backend.prod.Dockerfile
# Multi-stage build:
#   - Stage "builder": install build tools + compile dependencies
#   - Stage "runtime": image bersih tanpa compiler, jalankan sebagai non-root

# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/backend /build

# Install ke prefix terpisah agar bisa di-copy ke stage runtime
RUN pip install --no-cache-dir --prefix=/install .


# --- Stage 2: Runtime ---
FROM python:3.11-slim AS runtime

# Hanya install runtime dependency — tidak ada compiler di production image
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Buat non-root user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser

# Salin package yang sudah terinstall dari builder
COPY --from=builder /install /usr/local

# Salin source code
WORKDIR /app
COPY --from=builder /build /app

# Salin entrypoint script
COPY deploy/docker/entrypoints/api.sh /entrypoints/api.sh
RUN chmod +x /entrypoints/api.sh

# Set kepemilikan ke appuser
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# CMD menggunakan api.sh — TRUSTED_PROXY_IPS wajib diset di docker-compose
# Jangan override dengan --forwarded-allow-ips=* di sini
CMD ["/entrypoints/api.sh"]
