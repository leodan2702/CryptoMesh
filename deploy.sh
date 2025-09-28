#!/bin/bash
docker network create -d bridge cryptomesh-net || true  
echo "CryptoMesh network is ready"
# Deploy the MictlanX router
echo "Deploying MictlanX router..."
./deploy_router.sh

docker compose -f ./docker-compose.yml down || true
echo "Building and deploying CryptoMesh service..."
chmod +x ./reabuild.sh && ./rebuild.sh
docker compose -f docker-compose.yml up -d --build
echo "CryptoMesh service was deployed..."

# API="http://localhost:19000/docs"
# DEADLINE=$((SECONDS + 180))   # timeout after 180s; adjust as needed

