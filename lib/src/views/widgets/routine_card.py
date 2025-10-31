import flet as ft

from lib.src.models.db.models import Routine
from lib.src.views.widgets.message_box import MessageBox

class RoutineCard(ft.Container):
    _routine: Routine

    def _animation(self, e: ft.ControlEvent) -> None:
        e.control.content.scale = 1.1 if e.data == "true" else 1.0
        e.control.content.update()

    def _onclick(self, e: ft.ControlEvent) -> None:
        print("RoutineCard clicked:", self._routine)
        if self.page is not None:
            self.page.open(
                MessageBox(
                    title=self._routine.routine_name,
                    dsc=self._routine.description if self._routine.description else "Nenhuma descrição fornecida.",
                    script=self._routine.directory_path,
                    )
                )

    def __init__(self, routine: Routine):
        self._routine = routine
        super().__init__(
            on_hover=self._animation,
            on_click=self._onclick,
            content=ft.Card(
                animate_scale=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_IN_OUT_QUAD),
                elevation=5,
                shadow_color="#272727",
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(name=routine.category.icon, size=20),
                            ft.Text(
                                routine.routine_name,
                                style=ft.TextThemeStyle.BODY_MEDIUM,
                                text_align=ft.TextAlign.CENTER,
                                )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=ft.padding.all(10),
                )
            ) 
        )