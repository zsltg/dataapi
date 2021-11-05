"""Data Router"""
import typing
import datetime
import fastapi
import fastapi_pagination
from fastapi import encoders
from motor import motor_asyncio

from dataapi import utils
from dataapi.services import mongodb
from dataapi.models import dialog_model
from dataapi.controllers import dialog_controller

router = fastapi.APIRouter()


@router.get(
    "/data/",
    response_model=fastapi_pagination.LimitOffsetPage[dialog_model.DialogModel],
    responses={500: {"model": None}},
)
async def fetch_dialogs(
    language: typing.Optional[str] = None,
    customer_id: typing.Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
) -> utils.OrjsonResponse:
    """
    Fetch dialogs in bulk.

    - **language**: language of the dialogs to return (optional)
    - **customer_id**: return only dialogs for this customer id (optional)
    - **limit**: maximum number of dialogs to return
    - **offset**: number of dialogs to skip
    """
    return await dialog_controller.fetch_dialogs(
        db, language, customer_id, limit, offset
    )


@router.get(
    "/data/{customer_id}/{dialog_id}",
    responses={403: {"model": None}, 404: {"model": None}, 500: {"model": None}},
)
async def fetch_dialog(
    customer_id: str,
    dialog_id: str,
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
) -> utils.OrjsonResponse:
    """
    Fetch a dialog.

    - **customer_id**: customer id of the dialog to return
    - **dialog_id**: dialog id of the dialog to return
    """
    return await dialog_controller.fetch_dialog(db, customer_id, dialog_id)


@router.post(
    "/data/{customer_id}/{dialog_id}",
    response_description="Add new dialog",
    response_model=dialog_model.DialogBaseModel,
    status_code=201,
    responses={409: {"model": None}, 500: {"model": None}},
)
async def create_dialog(
    customer_id: str,
    dialog_id: str,
    dialog_body: dialog_model.DialogBaseModel = fastapi.Body(...),
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
) -> utils.OrjsonResponse:
    """
    Create a dialog.

    - **customer_id**: customer id of the dialog to create
    - **dialog_id**: dialog id of the dialog to create
    """
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


@router.delete(
    "/data/{customer_id}/{dialog_id}",
    responses={404: {"model": None}, 500: {"model": None}},
)
async def remove_dialog(
    customer_id: str,
    dialog_id: str,
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
) -> utils.OrjsonResponse:
    """
    Remove a dialog.

    - **customer_id**: customer id of the dialog to remove
    - **dialog_id**: dialog id of the dialog to remove
    """
    return await dialog_controller.remove_dialog(db, customer_id, dialog_id)
