from rpl_users.src.dtos.role import RoleResponseDTO
from rpl_users.src.dtos.university import UniversityResponseDTO
from rpl_users.src.repositories.roles import RolesRepository
from rpl_users.src.repositories.universities import UniversitiesRepository
from sqlalchemy.orm import Session


class CoursesService:
    def __init__(self, db_session: Session):
        # self.users_repo = UsersRepository(db_session)
        # self.courses_repo = CoursesRepository(db_session)
        # self.course_users_repo = CourseUsersRepository(db_session)
        self.roles_repo = RolesRepository(db_session)
        self.universities_repo = UniversitiesRepository(db_session)

    # =============================================================================

    def get_roles(self) -> list[RoleResponseDTO]:
        return self.roles_repo.get_all()

    def get_universities(self) -> list[UniversityResponseDTO]:
        return self.universities_repo.get_all()
