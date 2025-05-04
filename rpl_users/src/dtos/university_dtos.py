from pydantic import BaseModel

from rpl_users.src.repositories.models.university import University


class UniversityResponseDTO(BaseModel):
    id: int
    name: str
    degrees: list[str]

    @classmethod
    def from_university(cls, university: "University") -> "UniversityResponseDTO":
        return cls(
            id=university.id,
            name=university.name,
            degrees=university.get_degrees(),
        )
