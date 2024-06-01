from motor.motor_asyncio import AsyncIOMotorClient


class TaskRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient, collection_name: str = "task"):
        self.mongo_client = mongo_client
        self.collection_name = collection_name

    @property
    def collection(self):
        return self.mongo_client[self.collection_name]

    async def get_list(self) -> list[dict]:
        cursor = self.collection.find()
        return [task async for task in cursor]

    async def get(self, task_id: str) -> dict | None:
        return await self.collection.find_one({"_id": task_id})

    async def create(self, data_to_create: dict) -> dict:
        result = await self.collection.insert_one(data_to_create)
        return await self.get(result.inserted_id)

    async def update(self, task_id: str, data_to_update: dict) -> dict | None:
        result = await self.collection.update_one({"_id": task_id}, {"$set": data_to_update})
        if result.modified_count == 0:
            return None
        return await self.get(task_id)

    async def delete(self, task_id: str) -> dict | None:
        result = await self.collection.delete_one({"_id": task_id})
        if result.deleted_count == 0:
            return None
        return {"_id": task_id}
