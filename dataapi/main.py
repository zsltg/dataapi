"""DataAPI Main"""
import fastapi
import fastapi_pagination

import dataapi
from dataapi.routers import data_router, consent_router
from dataapi.services import mongodb

app = fastapi.FastAPI(
    title="DataAPI",
    description="Data API for chatbots",
    version=dataapi.__version__,
)

app.add_event_handler("startup", mongodb.connect)
app.add_event_handler("shutdown", mongodb.disconnect)
app.include_router(data_router.router)
app.include_router(consent_router.router)
fastapi_pagination.add_pagination(app)
