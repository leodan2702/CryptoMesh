from fastapi import APIRouter, status
import time as T

from cryptomesh.log.logger import get_logger
from cryptomesh.errors import handle_crypto_errors


L = get_logger(__name__)
router = APIRouter()

@router.get(
    "/health",
    status_code = status.HTTP_200_OK,
    summary     = "Health Check",
    description = "Simple health check endpoint."
)
@handle_crypto_errors
async def healthcheck():
    """Simple health check endpoint."""
    return {"status": "ok"}