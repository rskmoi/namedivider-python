from pydantic import BaseModel, validator
from typing import List


class DivisionRequest(BaseModel):
    names: List[str]

    @validator("names")
    def validate_names(cls, v):
        if len(v) > 1000:
            raise ValueError(f"You can only divide up to 1000 names at a time. length: {len(v)}")

        for idx, _v in enumerate(v):
            if len(_v) < 2:
                raise ValueError(f"Name length needs at least 2 chars. idx: {idx}, name: {_v}")
        return v


class ViewDividedName(BaseModel):
    family: str
    given: str
    separator: str
    score: float
    algorithm: str


class DivisionResult(BaseModel):
    divided_names: List[ViewDividedName]