from fastapi import FastAPI
from namedivider import NameDivider
from controller import division_controller
from controller.model import DivisionRequest

app = FastAPI()
divider = NameDivider()


@app.get("/health")
def health_check():
    return {"Health": "OK"}


@app.post("/divide")
def divide(division_request: DivisionRequest):
    return division_controller.divide(divider=divider, division_request=division_request)