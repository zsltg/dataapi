"""Dialog Model"""
import typing
import pydantic
import pybson
import datetime


class PyObjectId(pybson.ObjectId):
    @classmethod
    def __get_validators__(cls) -> typing.Generator[typing.Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v) -> pybson.ObjectId:
        if not pybson.ObjectId.is_valid(v):
            raise ValueError("Invalid Object ID")
        return pybson.ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DialogBaseModel(pydantic.BaseModel):
    text: str = pydantic.Field(...)
    language: str = pydantic.Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {pybson.ObjectId: str}
        schema_extra = {
            "example": {
                "text": "Lorem ipsum dolor sit amet",
                "language": "EN",
            }
        }


class DialogModel(DialogBaseModel):
    dialog_id: str = pydantic.Field(alias="_id")
    customer_id: str = pydantic.Field(...)
    consent_received = False
    date: datetime.datetime = pydantic.Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {pybson.ObjectId: str}
        schema_extra = {
            "example": {
                "dialog_id": "51d62c8e-4b81-4b1b-a288-bfd6ab2fa1bc",
                "customer_id": "johndoe",
                "text": "Lorem ipsum dolor sit amet",
                "language": "EN",
            }
        }
