# utils.py
from pydantic import BaseModel, constr

def trim_string(value: str) -> str:
    return value.strip() if isinstance(value, str) else value

class TrimmedBaseModel(BaseModel):
    class Config:
        # Automatically trim whitespace from string fields
        @staticmethod
        def validate_string(v):
            return trim_string(v)

        # Define any specific string field type that needs trimming
        @classmethod
        def __get_validators__(cls):
            yield cls.validate_string
