from typing import TypeVar, Generic, Type, Union, Optional, List
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from cryptomesh.log.logger import get_logger

T = TypeVar("T", bound=BaseModel)
L = get_logger(__name__)

class BaseRepository(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection, model: Type[T]):
        self.collection = collection
        self.model = model

    async def find_one(self, query: dict) -> Optional[T]:
        try:
            doc = await self.collection.find_one(query)
            return self.model(**doc) if doc else None
        except PyMongoError as e:
            L.error({"error": str(e)})
            raise HTTPException(status_code=500, detail="Database error in find_one")

    async def create(self, data: T) -> Optional[T]:
        try:
            result = await self.collection.insert_one(data.model_dump(by_alias=True, exclude_unset=True))
            if result.inserted_id:
                return data
            return None
        except PyMongoError as e:
            L.error({"error": str(e)})
            raise HTTPException(status_code=500, detail="Database error in create")

    async def get_all(self) -> List[T]:
        try:
            docs = []
            cursor = self.collection.find({})
            async for doc in cursor:
                docs.append(self.model(**doc))
            return docs
        except PyMongoError as e:
            L.error({"error": str(e)})
            raise HTTPException(status_code=500, detail="Database error in find_all")

    async def update(self, query: dict, updates: Union[dict, T]) -> Optional[T]:
        try:
            if isinstance(updates, BaseModel):
                updates = updates.model_dump(by_alias=True, exclude_unset=True)

            updated_doc = await self.collection.find_one_and_update(
                query, {"$set": updates}, return_document=True
            )
            return self.model(**updated_doc) if updated_doc else None
        except PyMongoError as e:
            L.error({"error": str(e)})
            raise HTTPException(status_code=500, detail="Database error in update")

    async def delete(self, query: dict) -> bool:
        try:
            result = await self.collection.delete_one(query)
            return result.deleted_count > 0
        except PyMongoError as e:
            L.error({"error": str(e)})
            raise HTTPException(status_code=500, detail="Database error in delete")


    async def get_by_id(self, id_value: str, id_field: str = "service_id") -> Optional[T]:
        try:
            document = await self.collection.find_one({id_field: id_value})
            return self.model(**document) if document else None
        except PyMongoError as e:
            L.error({"error": str(e)})
            raise HTTPException(status_code=500, detail="Database error in get_by_id")
