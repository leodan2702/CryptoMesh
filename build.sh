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

# Transformar tag GitHub a convención de Docker
VERSION="${GITHUB_TAG#v}"
# Reemplazar
VERSION="${VERSION/-alpha/a0}"
VERSION="${VERSION/-beta/b0}"
VERSION="${VERSION/-rc/rc0}"

# Construcción de la imagen
echo "🚀 Construyendo imagen Docker: $IMAGE_NAME:api-$VERSION"
docker build -t "$IMAGE_NAME:api-$VERSION" .

echo "✅ Imagen construida correctamente: $IMAGE_NAME:api-$VERSION"
