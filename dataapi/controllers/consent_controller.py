import pymongo
import fastapi
from motor import motor_asyncio
from fastapi import responses

from dataapi import utils
from dataapi.models import dialog_model
from dataapi.services import mongodb


async def record_consent(
    db: motor_asyncio.AsyncIOMotorClient, dialog_id: str, consent: bool
):
    if consent:
        result = await db.chatbot.dialog.update_one(
            {"_id": dialog_id}, {"$set": {"consent_received": consent}}
        )
        if result.matched_count:
            return utils.OrjsonResponse(status_code=fastapi.status.HTTP_200_OK)
        else:
            return utils.OrjsonResponse(status_code=fastapi.status.HTTP_404_NOT_FOUND)
    else:
        result = await db.chatbot.dialog.delete_one({"_id": dialog_id})
        if result.deleted_count:
            return utils.OrjsonResponse(status_code=fastapi.status.HTTP_200_OK)
        else:
            return utils.OrjsonResponse(status_code=fastapi.status.HTTP_404_NOT_FOUND)
