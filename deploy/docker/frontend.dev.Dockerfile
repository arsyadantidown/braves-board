# =============================================================================
# frontend.dev.Dockerfile
# Environment development:
#   - Hot-reload Vite aktif
#   - Berjalan sebagai non-root user
# =============================================================================

FROM node:20-alpine

WORKDIR /app

# Install dependencies terlebih dahulu (manfaatkan layer cache)
COPY src/frontend/package*.json ./
RUN npm install

COPY src/frontend .

# Buat non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
