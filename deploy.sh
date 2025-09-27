#!/bin/bash
docker network create -d bridge cryptomesh-net || true  
echo "CryptoMesh network is ready"
# Deploy the MictlanX router
echo "Deploying MictlanX router..."
./deploy_router.sh

docker compose -f ./docker-compose.yml down || true
docker compose -f docker-compose.yml up -d --build
echo "CryptoMesh service was deployed..."

API="http://localhost:19000/docs"
DEADLINE=$((SECONDS + 180))   # timeout after 180s; adjust as needed

# for i in {1..20}; do
#     if curl -s http://localhost:19000/docs > /dev/null; then
#         echo "✅ CryptoMesh service is successfully deployed"
#         break
#     fi
#     sleep 3
# done