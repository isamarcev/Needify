from abc import ABC, abstractmethod

from pymongo import IndexModel

from src.apps.utils.database import ThreadMongoSingleton


class BaseUserDatabase(ABC):
    @abstractmethod
    async def get_users(self):
        raise NotImplementedError()

    @abstractmethod
    async def insert_user(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def get_user(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_telegram_id(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_username(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def update_user(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def delete_user(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_filter(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def setup_indexes(self, *args, **kwargs):
        raise NotImplementedError()


class MongoDBUserRepository(BaseUserDatabase):
    def __init__(self, mongo_conn: str, mongo_db: str, collection_name: str = "users"):
        self.mongo_client = ThreadMongoSingleton(mongo_conn, mongo_db)
        self.collection_name = collection_name

    @property
    def collection(self):
        return self.mongo_client[self.collection_name]

    async def get_users(self) -> list[dict]:
        cursor = self.collection.find()
        return [user async for user in cursor]

    async def insert_user(self, **kwargs) -> dict:
        result = await self.collection.insert_one(kwargs)
        return await self.get_user(result.inserted_id)

    async def get_user(self, user_id: str) -> dict | None:
        return await self.collection.find_one({"_id": user_id})

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        return await self.collection.find_one({"telegram_id": telegram_id})

    async def get_user_by_username(self, username: str) -> dict | None:
        return await self.collection.find_one({"username": username})

    async def get_user_by_filter(self, filter_: dict) -> dict | None:
        return await self.collection.find_one(filter_)

    async def update_user(self, telegram_id: int, dict_to_update: dict) -> None:
        result = await self.collection.update_one(
            {"telegram_id": telegram_id}, {"$set": dict_to_update}
        )
        if result.modified_count == 0:
            return None
        else:
            return await self.get_user_by_telegram_id(telegram_id)

    async def delete_user(self, telegram_id: int) -> None:
        await self.collection.delete_one({"telegram_id": telegram_id})

    async def setup_indexes(self, indexes: list[IndexModel]):
        await self.collection.create_indexes(indexes)
