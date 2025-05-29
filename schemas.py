from pydantic import BaseModel, Field, validator
from typing import List, Optional
import requests


class CreateCat(BaseModel):
    name: str
    experience: int = Field(..., ge=0)
    breed: str
    salary: float = Field(..., ge=0)

    @validator('breed')
    def validate_breed(cls, v):
        response = requests.get("https://api.thecatapi.com/v1/breeds")
        if response.status_code == 200:
            breeds = [b["name"].lower() for b in response.json()]
            if v.lower() not in breeds:
                raise ValueError("Invalid cat breed")
            return v
        raise ValueError("Could not validate breed (TheCatAPI unreachable)")


class UpdateCatSalary(BaseModel):
    salary: float = Field(..., ge=0)


class CatOut(BaseModel):
    id: int
    name: str
    experience: int
    breed: str
    salary: float

    class Config:
        orm_mode = True


class CreateTarget(BaseModel):
    name: str
    country: str
    notes: Optional[str] = ""


class TargetOut(BaseModel):
    id: int
    name: str
    country: str
    notes: str
    is_complete: bool

    class Config:
        orm_mode = True


class CreateMission(BaseModel):
    name: str
    targets: List[CreateTarget]

    @validator("targets")
    def validate_targets_length(cls, v):
        if not (1 <= len(v) <= 3):
            raise ValueError("Mission must have between 1 and 3 targets")
        return v


class AssignCatToMission(BaseModel):
    cat_id: int


class MissionOut(BaseModel):
    id: int
    name: str
    is_complete: bool
    cat: Optional[CatOut]
    targets: List[TargetOut]

    class Config:
        orm_mode = True


class UpdateTargetNotes(BaseModel):
    notes: str


class MarkTargetComplete(BaseModel):
    is_complete: bool
