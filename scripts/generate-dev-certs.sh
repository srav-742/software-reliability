#!/bin/sh
set -e

mkdir -p nginx/certs

if [ ! -f nginx/certs/server.crt ] || [ ! -f nginx/certs/server.key ]; then
    echo "Generating self-signed SSL certificate for local development..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/certs/server.key \
        -out nginx/certs/server.crt \
        -subj "/C=US/ST=State/L=City/O=Development/OU=IT/CN=localhost"
    echo "Certificates successfully generated in nginx/certs/"
else
    echo "SSL certificates already exist in nginx/certs/"
fi
