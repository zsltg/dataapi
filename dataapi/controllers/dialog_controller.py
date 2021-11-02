import pymongo
import fastapi
from motor import motor_asyncio
from fastapi import responses

from dataapi.models import dialog_model
from dataapi.services import mongodb


async def create_dialog(
    db: motor_asyncio.AsyncIOMotorClient, dialog_entry: dialog_model.DialogModel
):
    try:
        new_dialog = await db.chatbot.dialog.insert_one(dialog_entry)
    except pymongo.errors.DuplicateKeyError:
        return responses.JSONResponse(status_code=fastapi.status.HTTP_409_CONFLICT)
    created_dialog = await db.chatbot.dialog.find_one({"_id": new_dialog.inserted_id})
    return responses.JSONResponse(
        status_code=fastapi.status.HTTP_201_CREATED, content=created_dialog
    )


async def remove_dialog(db: motor_asyncio.AsyncIOMotorClient, dialog_id: str):
    await db.chatbot.dialog.delete_one({"_id": dialog_id})
    return responses.JSONResponse(status_code=fastapi.status.HTTP_204_NO_CONTENT)
