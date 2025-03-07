from cryptomesh.repositories import ServicesRepository
from cryptomesh.models import ServiceModel

class ServicesService:
    def __init__(self,repository:ServicesRepository):
        self.repository = repository

    async def get_all_services(self) -> list[ServiceModel]:
        """
        Retrieve all services from the repository.
        """
        return await self.repository.find_all()

    async def create_service(self, service: ServiceModel) -> ServiceModel:
        """
        Create a new service using the repository.
        """
        return await self.repository.create(service)
