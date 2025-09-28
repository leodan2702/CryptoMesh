set -euo pipefail

# Nombre base de la imagen
IMAGE_NAME="leogarcia10/cryptomesh"

# Verificar que se pase un tag
if [ $# -lt 1 ]; then
  echo "Uso: $0 <tag_github>"
  echo "Ejemplo: $0 v0.0.1-alpha"
  exit 1
fi

GITHUB_TAG="$1"

# Transformar tag GitHub a convención Docker
VERSION="${GITHUB_TAG#v}"
VERSION="${VERSION/-alpha/a0}"
VERSION="${VERSION/-beta/b0}"
VERSION="${VERSION/-rc/rc0}"


# Publicar en Docker Hub
echo "📤 Publicando imagen en Docker Hub: $IMAGE_NAME:api-$VERSION"
docker push "$IMAGE_NAME:api-$VERSION"

echo "✅ Imagen publicada correctamente: $IMAGE_NAME:api-$VERSION"
