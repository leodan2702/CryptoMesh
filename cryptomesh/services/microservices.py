from cryptomesh.repositories.microservices import MicroservicesRepository
from cryptomesh.models import MicroserviceModel


class MicroservicesService:
    def __init__(self, repository: MicroservicesRepository):
        self.repository = repository

    async def get_all_microservices(self) -> list[MicroserviceModel]:
        return await self.repository.find_all()
