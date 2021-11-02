import typing
import pymongo
import fastapi
import fastapi_pagination
from motor import motor_asyncio
from fastapi import responses

from dataapi.models import dialog_model
from dataapi.services import mongodb
from dataapi import utils


async def fetch_dialogs(
    db: motor_asyncio.AsyncIOMotorClient,
    params: fastapi_pagination.Params,
    language: typing.Optional[str] = None,
    customer_id: typing.Optional[str] = None,
):
    query = {
        "$and": [{"consent_received": True}]
    }  # type: typing.Dict[str, typing.List[typing.Any]]
    expression = {"$or": []}  # type: typing.Dict[str, typing.List[typing.Any]]
    if language:
        expression["$or"].append({"language": language})
    if customer_id:
        expression["$or"].append({"customer_id": customer_id})
    if expression["$or"]:
        query["$and"].append(expression)
    cursor = db.chatbot.dialog.find(query)
    cursor.sort("date", -1)
    hits = await cursor.to_list(length=None)
    content = fastapi_pagination.paginate(hits, params)
    return utils.OrjsonResponse(
        status_code=fastapi.status.HTTP_200_OK, content=content.dict()
    )


async def fetch_dialog(
    db: motor_asyncio.AsyncIOMotorClient, customer_id: str, dialog_id: str
):
    dialog_entry = await db.chatbot.dialog.find_one(
        {"_id": dialog_id, "customer_id": customer_id}
    )
    if dialog_entry:
        if dialog_entry["consent_received"]:
            return utils.OrjsonResponse(
                status_code=fastapi.status.HTTP_200_OK, content=dialog_entry
            )
        else:
            return utils.OrjsonResponse(status_code=fastapi.status.HTTP_403_FORBIDDEN)
    else:
        return utils.OrjsonResponse(status_code=fastapi.status.HTTP_404_NOT_FOUND)


async def create_dialog(
    db: motor_asyncio.AsyncIOMotorClient, dialog_entry: dialog_model.DialogModel
):
    try:
        new_dialog = await db.chatbot.dialog.insert_one(dialog_entry)
    except pymongo.errors.DuplicateKeyError:
        return utils.OrjsonResponse(status_code=fastapi.status.HTTP_409_CONFLICT)
    created_dialog = await db.chatbot.dialog.find_one({"_id": new_dialog.inserted_id})
    return utils.OrjsonResponse(
        status_code=fastapi.status.HTTP_201_CREATED, content=created_dialog
    )


async def remove_dialog(
    db: motor_asyncio.AsyncIOMotorClient, customer_id: str, dialog_id: str
):
    await db.chatbot.dialog.delete_one({"_id": dialog_id, "customer_id": customer_id})
    return utils.OrjsonResponse(status_code=fastapi.status.HTTP_204_NO_CONTENT)
