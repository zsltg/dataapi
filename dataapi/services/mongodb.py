"""MongoDB Service"""
from motor import motor_asyncio

from dataapi import config

settings = config.get_settings()


class DataBase:
    client: motor_asyncio.AsyncIOMotorClient = None


db = DataBase()


async def get_database() -> motor_asyncio.AsyncIOMotorClient:
    return db.client


async def connect():
    db.client = motor_asyncio.AsyncIOMotorClient(
        str("mongodb://{}:{}".format(settings.mongodb_url, settings.mongodb_port))
    )


async def disconnect():
    db.client.close()
