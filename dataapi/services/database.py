from motor import motor_asyncio

# from .. import main

MONGODB_URL = "mongodb://localhost:27017"
motor_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
client = motor_client.dialogs
# client = None

# @main.app.on_event("startup")
# async def setup():
#    motor_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
#    client = motor_client.dialogs
