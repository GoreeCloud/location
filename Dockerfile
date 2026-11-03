FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 XDG_DATA_HOME=/data
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . && useradd --system --uid 10001 --create-home gclocation \
    && mkdir -p /data && chown gclocation:gclocation /data
USER gclocation
EXPOSE 8123
CMD ["gclocation", "serve", "--host", "0.0.0.0", "--port", "8123", "--i-understand-network-exposure"]
