from pydantic import BaseModel


class RoleResponseDTO(BaseModel):
    id: int
    name: str
    permissions: list[str]
