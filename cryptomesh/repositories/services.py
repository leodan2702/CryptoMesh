
from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import ServiceModel

class ServicesRepository():
    def __init__(self,collection:AsyncIOMotorCollection):
        self.collection = collection

    async def find_all(self) -> list[ServiceModel]:
        """
        Retrieve all service documents from the MongoDB collection,
        convert them to ServiceModel instances, and return as a list.
        """
        services = []
        cursor = self.collection.find({})
        async for document in cursor:
            # Convert MongoDB ObjectId to string for the Pydantic model
            document["id"] = str(document.get("_id"))
            services.append(ServiceModel(**document))
        return services

    async def create(self, service: ServiceModel) -> ServiceModel:
        """
        Insert a new service document into the MongoDB collection.
        Returns the created ServiceModel with its assigned id.
        """
        # Convert the ServiceModel to a dictionary.
        service_dict = service.model_dump(exclude_unset=True)
        result = await self.collection.insert_one(service_dict)
        service_dict["id"] = str(result.inserted_id)
        return ServiceModel(**service_dict)