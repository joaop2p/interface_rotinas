from typing import Sequence
from lib.src.models.db.models import Routine
from lib.src.services.routines import RoutinesService


class RoutinesController:
    def __init__(self):
        self.service = RoutinesService()

    def get_all_routines(self) -> Sequence[Routine]:
        return self.service.get_all_routines()
    
    def get_by_category_id(self, category_id: int) -> Sequence[Routine]:
        return self.service.get_by_category_id(category_id)

    def insert_routine(self, name: str, path: str, desc: str, category_id: int) -> Routine:
        routine = Routine(
            routine_name=name,
            directory_path=path,
            description=desc,
            category_id=category_id
        )
        return self.service.insert_routine(routine)