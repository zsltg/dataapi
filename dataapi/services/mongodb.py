from motor import motor_asyncio

from dataapi import config

SETTINGS = config.get_settings()


class DataBase:
    client: motor_asyncio.AsyncIOMotorClient = None


DB = DataBase()


async def get_database() -> motor_asyncio.AsyncIOMotorClient:
    return DB.client


async def connect():
    DB.client = motor_asyncio.AsyncIOMotorClient(
        str("mongodb://{}:{}".format(SETTINGS.mongodb_url, SETTINGS.mongodb_port))
    )


async def disconnect():
    DB.client.close()
