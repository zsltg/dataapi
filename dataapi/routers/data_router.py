import typing
import datetime
import fastapi
import fastapi_pagination
from fastapi import encoders
from motor import motor_asyncio

from dataapi.services import mongodb
from dataapi.models import dialog_model
from dataapi.controllers import dialog_controller

router = fastapi.APIRouter()


@router.get(
    "/data/",
    response_model=fastapi_pagination.LimitOffsetPage[dialog_model.DialogModel],
)
async def fetch_dialogs(
    limit: int = 100,
    offset: int = 0,
    language: typing.Optional[str] = None,
    customer_id: typing.Optional[str] = None,
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
):
    return await dialog_controller.fetch_dialogs(
        db, limit, offset, language, customer_id
    )


@router.get("/data/{customer_id}/{dialog_id}", responses={403: {"model": None}, 404: {"model": None}})
async def fetch_dialog(
    customer_id: str,
    dialog_id: str,
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
):
    return await dialog_controller.fetch_dialog(db, customer_id, dialog_id)


@router.post(
    "/data/{customer_id}/{dialog_id}",
    response_description="Add new dialog",
    response_model=dialog_model.DialogBaseModel,
    status_code=201,
    responses={409: {"model": None}}
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
            date=datetime.datetime.utcnow(),
        )
    )
    return await dialog_controller.create_dialog(db, dialog_entry)


@router.delete("/data/{customer_id}/{dialog_id}",
    responses={404: {"model": None}},
)
async def remove_dialog(
    customer_id: str,
    dialog_id: str,
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
):
    return await dialog_controller.remove_dialog(db, customer_id, dialog_id)
