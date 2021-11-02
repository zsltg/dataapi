"""DataAPI Utilities"""
import typing
import orjson
from fastapi import responses


class OrjsonResponse(responses.JSONResponse):
    """fastapi response with orjson"""

    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content)  # pylint: disable=no-member
