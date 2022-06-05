from __future__ import annotations

from controller import division_controller
from controller.model import DivisionRequest, DivisionResult
from fastapi import FastAPI

from namedivider import NameDivider

app = FastAPI()
divider = NameDivider()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"Health": "OK"}


@app.post("/divide")
def divide(division_request: DivisionRequest) -> DivisionResult:
    return division_controller.divide(
        divider=divider, division_request=division_request
    )
