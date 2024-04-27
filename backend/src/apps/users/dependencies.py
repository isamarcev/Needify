from src.apps.users.manager import UserManager
from src.apps.users.database import MongoDBUserDatabase
from src.core.database import async_mongo


def get_user_database():
    user_database = MongoDBUserDatabase(mongo_client=async_mongo, collection_name="users")
    return user_database


def get_user_manager() -> UserManager:
    user_database = get_user_database()
    return UserManager(user_database)


user_manager = get_user_manager()
