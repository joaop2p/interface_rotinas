from typing import Sequence
from lib.src.dao.routines import RoutinesDAO
from lib.src.models.db.models import Routine


class RoutinesService:
    def __init__(self):
        self.dao = RoutinesDAO()

    def get_all_routines(self) -> Sequence[Routine]:
        return self.dao.get_all_routines()