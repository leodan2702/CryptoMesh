#!/bin/bash
URL=$1
for i in {1..20}; do
    if curl -s $URL > /dev/null; then
        echo "✅ CryptoMesh service is successfully deployed"
        break
    fi
    sleep 3
done
# echo "Waiting for service at $URL..."
# until $(curl --output /dev/null --silent --head --fail "$URL"); do
#     echo "$URL is not available yet. Retrying in 5 seconds..."
#     sleep 5
# done
# echo "Service is up!"