FROM python:3.11-slim

WORKDIR /app

# 1. Install build dependencies and ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libc-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 2. Pip install with trusted hosts for Zscaler
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# 3. Remove build dependencies to keep the image small
RUN apt-get purge -y --auto-remove gcc python3-dev libc-dev

# 4. Copy the Mac .pem cert and rename to .crt for Debian to process it
COPY corporate-root-ca.pem /usr/local/share/ca-certificates/corporate-root-ca.crt
RUN update-ca-certificates

# 5. Tell Python to use the newly updated system cert bundle
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]