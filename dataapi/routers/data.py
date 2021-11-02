import fastapi
from fastapi import responses, encoders
import pymongo
from motor import motor_asyncio

# from dataapi.services import database
from dataapi.services import mongodb
from dataapi.models import dialog

# from .. import main

router = fastapi.APIRouter()

# def get_db_client() -> motor_asyncio.AsyncIOMotorClient:
#    return database.client
# db = database.client


@router.post(
    "/data/{customer_id}/{dialog_id}",
    response_description="Add new dialog",
    response_model=dialog.DialogBaseModel,
)
async def create_dialog(
    customer_id: str,
    dialog_id: str,
    dialog_body: dialog.DialogBaseModel = fastapi.Body(...),
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
):
    dialog_entry = encoders.jsonable_encoder(
        dialog.DialogModel(
            customer_id=customer_id,
            dialog_id=dialog_id,
            text=dialog_body.text,
            language=dialog_body.language,
        )
    )
    try:
        new_dialog = await db.dialogs["dialogs"].insert_one(dialog_entry)
    except pymongo.errors.DuplicateKeyError:
        return responses.JSONResponse(status_code=fastapi.status.HTTP_409_CONFLICT)
    created_dialog = await db.dialogs["dialogs"].find_one(
        {"_id": new_dialog.inserted_id}
    )
    return responses.JSONResponse(
        status_code=fastapi.status.HTTP_201_CREATED, content=created_dialog
    )
