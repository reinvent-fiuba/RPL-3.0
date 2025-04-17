from pydantic import BaseModel


class UniversityResponseDTO(BaseModel):
    id: int
    name: str
    degrees: list[str]
