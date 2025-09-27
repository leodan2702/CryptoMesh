#!/bin/bash
URL=$1
echo "Waiting for service at $URL..."
for i in {1..20}; do
    if curl -s $URL > /dev/null; then
        echo "✅ CryptoMesh service is successfully deployed"
        break
    fi
    echo "Waiting for service... $URL"
    sleep 3
done
