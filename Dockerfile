# Stage 1: Base build stage
FROM python:3.13-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --prefer-binary --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim
WORKDIR /app

# Si usas xvfb aún para algo, mantenlo, sino elimínalo también
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY . .

RUN sed -i 's/\r$//' /app/entrypoint.prod.sh /app/entrypoint.worker.sh \
 && chmod +x /app/entrypoint.prod.sh /app/entrypoint.worker.sh

# Usuario no root
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["/app/entrypoint.prod.sh"]
