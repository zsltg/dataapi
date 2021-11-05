# pylint: disable=too-few-public-methods
"""DataAPI Configuration"""
from functools import lru_cache

import pydantic


@lru_cache()
def get_settings() -> object:
    """Get settings"""
    return Settings()


class Settings(pydantic.BaseSettings):
    """DataAPI Settings"""

    mongodb_url: str
    mongodb_port: str
    mongodb_timeout: str

    class Config:
        """Settings Configuration"""

        env_file = ".env"
