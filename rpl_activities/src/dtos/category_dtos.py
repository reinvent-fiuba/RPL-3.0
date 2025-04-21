from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryResponseDTO(BaseModel):
    id: int
    name: str
    description: str
    date_created: datetime
    last_updated: datetime
    active: bool


class CategoryCreationRequestDTO(BaseModel):
    name: str
    description: str


class CategoryUpdateRequestDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
