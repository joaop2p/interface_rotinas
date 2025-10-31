from typing import Iterable
from .routine_card import RoutineCard
from lib.src.models.db.models import Routine
import flet as ft

class RoutinesGrid(ft.GridView):
    def __init__(self, routines: Iterable[Routine], ref: ft.Ref[ft.GridView]) -> None:
        super().__init__(
            padding=ft.padding.all(20),
            max_extent=150,
            ref=ref,
            runs_count=2,
            spacing=10,
            height=300,
            run_spacing=10,
            controls=[
                RoutineCard(routine=routine)
                for routine in routines
            ],
        )