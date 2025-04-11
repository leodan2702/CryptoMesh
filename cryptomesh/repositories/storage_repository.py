from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional
from pymongo.errors import PyMongoError
from cryptomesh.models import StorageModel

class StorageRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, storage: StorageModel) -> Optional[StorageModel]:
        try:
            storage_dict = storage.dict(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(storage_dict)
            if result.inserted_id:
                return storage
            return None
        except PyMongoError as e:
            print(f"❌ Error al crear storage: {e}")
            return None

    async def get_all(self) -> List[StorageModel]:
        storage_list = []
        cursor = self.collection.find({})
        async for document in cursor:
            storage_list.append(StorageModel(**document))
        return storage_list

    async def get_by_id(self, storage_id: str) -> Optional[StorageModel]:
        document = await self.collection.find_one({"storage_id": storage_id})
        if document:
            return StorageModel(**document)
        return None

    async def update(self, storage_id: str, updates: dict) -> Optional[StorageModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"storage_id": storage_id},
                {"$set": updates},
                return_document=True  # Si usas pymongo>=3.6, podrías importar ReturnDocument.AFTER
            )
            if updated:
                return StorageModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error al actualizar storage: {e}")
            return None

    async def delete(self, storage_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"storage_id": storage_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error al eliminar storage: {e}")
            return False

