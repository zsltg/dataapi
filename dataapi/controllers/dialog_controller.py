"""Dialog Controller"""
import typing
import pymongo
import fastapi
import fastapi_pagination
from motor import motor_asyncio
from fastapi import responses

from dataapi import utils
from dataapi.models import dialog_model
from dataapi.services import mongodb


async def fetch_dialogs(
    db: motor_asyncio.AsyncIOMotorClient,
    language: typing.Optional[str] = None,
    customer_id: typing.Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> utils.OrjsonResponse:
    query = {
        "$and": [{"consent_received": True}]
    }  # type: typing.Dict[str, typing.List[typing.Union[typing.Dict[str, bool], typing.Dict[str, str]]]]
    if language:
        query["$and"].append({"language": language})
    if customer_id:
        query["$and"].append({"customer_id": customer_id})
    try:
        count = await db.chatbot.dialog.count_documents(query)
        cursor = db.chatbot.dialog.find(query)
    except pymongo.errors.ServerSelectionTimeoutError:
        return utils.OrjsonResponse(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    cursor.sort("date", -1).skip(offset).limit(limit)
    hits = await cursor.to_list(length=None)
    params = fastapi_pagination.LimitOffsetParams(limit=limit, offset=0)
    content = fastapi_pagination.paginate(hits, params, length_function=lambda _: count)
    content.offset = offset
    return utils.OrjsonResponse(
        status_code=fastapi.status.HTTP_200_OK, content=content.dict()
    )


async def fetch_dialog(
    db: motor_asyncio.AsyncIOMotorClient, customer_id: str, dialog_id: str
) -> utils.OrjsonResponse:
    try:
        dialog_entry = await db.chatbot.dialog.find_one(
            {"_id": dialog_id, "customer_id": customer_id}
        )
    except pymongo.errors.ServerSelectionTimeoutError:
        return utils.OrjsonResponse(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
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
) -> utils.OrjsonResponse:
    try:
        new_dialog = await db.chatbot.dialog.insert_one(dialog_entry)
    except pymongo.errors.DuplicateKeyError:
        return utils.OrjsonResponse(status_code=fastapi.status.HTTP_409_CONFLICT)
    except pymongo.errors.ServerSelectionTimeoutError:
        return utils.OrjsonResponse(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    created_dialog = await db.chatbot.dialog.find_one({"_id": new_dialog.inserted_id})
    return utils.OrjsonResponse(
        status_code=fastapi.status.HTTP_201_CREATED, content=created_dialog
    )


async def remove_dialog(
    db: motor_asyncio.AsyncIOMotorClient, customer_id: str, dialog_id: str
) -> utils.OrjsonResponse:
    try:
        result = await db.chatbot.dialog.delete_one(
            {"_id": dialog_id, "customer_id": customer_id}
        )
    except pymongo.errors.ServerSelectionTimeoutError:
        return utils.OrjsonResponse(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    if result.deleted_count:
        return utils.OrjsonResponse(status_code=fastapi.status.HTTP_200_OK)
    else:
        return utils.OrjsonResponse(status_code=fastapi.status.HTTP_404_NOT_FOUND)
