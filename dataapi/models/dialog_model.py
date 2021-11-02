import pydantic
import bson


class PyObjectId(bson.ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not bson.ObjectId.is_valid(v):
            raise ValueError("Invalid Object ID")
        return bson.ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DialogBaseModel(pydantic.BaseModel):
    text: str = pydantic.Field(...)
    language: str = pydantic.Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {bson.ObjectId: str}
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

    class Config:
        allow_population_by_field_name = True
        json_encoders = {bson.ObjectId: str}
        schema_extra = {
            "example": {
                "dialog_id": "51d62c8e-4b81-4b1b-a288-bfd6ab2fa1bc",
                "customer_id": "johndoe",
                "text": "Lorem ipsum dolor sit amet",
                "language": "EN",
            }
        }
