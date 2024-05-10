from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorClient


class BaseRepository(ABC):
    @abstractmethod
    async def get_list(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def create(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def delete(self, *args, **kwargs):
        pass


class BaseMongoRepository(BaseRepository):
    def __init__(self, mongo_client: AsyncIOMotorClient, collection_name: str):
        self.mongo_client = mongo_client
        self.collection_name = collection_name

    @property
    def collection(self):
        return self.mongo_client[self.collection_name]

    async def get_list(self, by_filter: dict | None = None):
        if by_filter:
            cursor = self.collection.find(by_filter)
        else:
            cursor = self.collection.find()
        return [obj_ async for obj_ in cursor]

    async def get_by_filter(self, by_filter: dict):
        return await self.collection.find_one(by_filter)

    async def get(self, obj_id: str):
        return await self.collection.find_one({"_id": obj_id})

    async def create(self, data_to_create: dict):
        result = await self.collection.insert_one(data_to_create)
        return await self.get(result.inserted_id)

    async def update(self, obj_id: str, data_to_update: dict):
        result = await self.collection.update_one(
            {"_id": obj_id}, {"$set": data_to_update}
        )
        if result.modified_count == 0:
            return None
        return await self.get(obj_id)

    async def delete(self, obj_id: str):
        result = await self.collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            return None
        return {"_id": obj_id}
