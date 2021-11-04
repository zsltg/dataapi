import fastapi

from fastapi import encoders
from motor import motor_asyncio

from dataapi import utils
from dataapi.services import mongodb
from dataapi.models import dialog_model
from dataapi.controllers import consent_controller

router = fastapi.APIRouter()


@router.post(
    "/consents/{dialog_id}",
    response_description="Record consent",
    responses={404: {"model": None}},
)
async def record_consent(
    dialog_id: str,
    consent_body: bool = fastapi.Body(...),
    db: motor_asyncio.AsyncIOMotorClient = fastapi.Depends(mongodb.get_database),
) -> utils.OrjsonResponse:
    """
    Record a consent.

    - **dialog_id**: record consent for the dialog with this id
    """
    return await consent_controller.record_consent(db, dialog_id, consent_body)
