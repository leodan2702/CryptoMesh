#!/bin/bash
URL=$1
echo "Waiting for service at $URL..."
echo "--------------------------------------------------"
for i in {1..20}; do
    echo -e "\n--- Attempt $i of 20 ---"
    if curl -f -s $URL; then
        echo "✅ CryptoMesh service is successfully deployed"
        exit 0
    fi
    echo "Waiting for service... $URL"
    sleep 3
done
echo -e "\n❌ Service did not become available after 20 attempts."
exit 1 # Exit with a failure code