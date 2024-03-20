import pydantic as pd


class Chip(pd.BaseModel):
    id: int
    chip: str


class GetChipsResponse(pd.BaseModel):
    chips: list[Chip]
