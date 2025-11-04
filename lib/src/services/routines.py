from typing import Sequence
from lib.src.dao.routines import RoutinesDAO
from lib.src.models.db.models import Routine


class RoutinesService:
    def __init__(self):
        self.dao = RoutinesDAO()

    def get_all_routines(self) -> Sequence[Routine]:
        return self.dao.get_all_routines()

    def get_by_id(self, routine_id: int) -> Routine | None:
        return self.dao.get_by_id(routine_id)

    def insert_routine(self, routine: Routine) -> Routine:
        return self.dao.insert_routine(routine)
    
    def delete_routine(self, routine: Routine) -> None:
        self.dao.delete_routine(routine)

    def update_routine(self, routine: Routine) -> Routine:
        return self.dao.update_routine(routine)