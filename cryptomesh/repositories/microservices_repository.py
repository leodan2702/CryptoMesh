from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import MicroserviceModel
from cryptomesh.repositories.base_repository import BaseRepository
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class MicroservicesRepository(BaseRepository[MicroserviceModel]):
    """
    Repositorio encargado de gestionar la colección 'microservices' en MongoDB.
    """
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, MicroserviceModel)

