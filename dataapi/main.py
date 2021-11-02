"""DataAPI Main"""
import fastapi

import dataapi
from dataapi.routers import data_router
from dataapi.services import mongodb

APP = fastapi.FastAPI(
    title="DataAPI",
    description="Data API for chatbots",
    version=dataapi.__version__,
)

APP.add_event_handler("startup", mongodb.connect)
APP.add_event_handler("shutdown", mongodb.disconnect)
APP.include_router(data_router.ROUTER)
