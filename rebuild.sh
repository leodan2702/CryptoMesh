readonly IMAGE_NAME="cryptomesh:api"
docker build -f ./Dockerfile -t $IMAGE_NAME .
docker compose -f docker-compose.yml down 
docker compose -f ./docker-compose.yml up -d