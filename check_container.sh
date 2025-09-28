#!/bin/bash
#!/bin/bash
CONTAINER_NAME="crypto-mesh-api" # Use your container's name
echo "Waiting for container '$CONTAINER_NAME' to be healthy..."

for i in {1..30}; do
    # Inspect the container's health status
    STATUS=$(docker inspect --format '{{.State.Health.Status}}' $CONTAINER_NAME)
    if [ "$STATUS" = "healthy" ]; then
        echo -e "\n✅ Container '$CONTAINER_NAME' is healthy!"
        exit 0
    fi
    printf '.'
    sleep 5
done

echo -e "\n❌ Container did not become healthy in time."
exit 1