from datetime import datetime
from pydantic import BaseModel


class CategoryCreationDTO(BaseModel):
    name: str
    description: str
    date_created: datetime
    last_updated: datetime
    active: bool
