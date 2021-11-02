import fastapi

from fastapi import encoders
from motor import motor_asyncio

from dataapi.services import mongodb
from dataapi.models import dialog_model
from dataapi.controllers import dialog_controller

ROUTER = fastapi.APIRouter()


@ROUTER.post(
    "/data/{customer_id}/{dialog_id}",
    response_description="Add new dialog",
    response_model=dialog_model.DialogBaseModel,
)
async def create_dialog(
    customer_id: str,
    dialog_id: str,
    dialog_body: dialog_model.DialogBaseModel = fastapi.Body(...),
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
):
    dialog_entry = encoders.jsonable_encoder(
        dialog_model.DialogModel(
            customer_id=customer_id,
            dialog_id=dialog_id,
            text=dialog_body.text,
            language=dialog_body.language,
        )
    )
    return await dialog_controller.create_dialog(db, dialog_entry)


@ROUTER.delete("/data/{dialog_id}")
async def remove_dialog(
    dialog_id: str,
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
):
    return await dialog_controller.remove_dialog(db, dialog_id)
