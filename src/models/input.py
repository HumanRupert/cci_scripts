from pydantic import BaseModel


class WorldbankInput(BaseModel):
    start: int
    end: int


class PewInput(BaseModel):
    path: str
