from typing import Sequence
from lib.src.models.db.models import Routine
from lib.src.services.routines import RoutinesService


class RoutinesController:
    def __init__(self):
        self.service = RoutinesService()

    def get_all_routines(self) -> Sequence[Routine]:
        return self.service.get_all_routines()