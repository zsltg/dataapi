"""DataAPI Main"""
from fastapi import FastAPI

import dataapi

app = FastAPI(
    title="DataAPI",  # pragma: no mutate
    description="Data API for chatbots",  # pragma: no mutate
    version=dataapi.__version__,  # pragma: no mutate
)  # pragma: no mutate


@app.get("/")  # pragma: no mutate
def read_root():
    """Root"""
    return {"Hello": "World"}
