import asyncio
import logging
from random import randint
from threading import Thread
from time import sleep
from typing import Iterable
from lib.config import Config
from lib.src.controllers.routines import RoutinesController
from lib.src.controllers.category import CategoryController
from lib.src.models.db.models import Routine
from lib.src.models.interfaces.view_template import ViewTemplate
import flet as ft
from lib.src.views.widgets.category_labels import CategoryLabels
from lib.src.views.widgets.routines_grid import RoutineCard, RoutinesGrid

class HomeView(ViewTemplate):
    _title = "Menu Inicial"
    _route = "/home"
    _TERMINAL_LIMIT = 100
    _grid_reference: ft.Ref[ft.GridView]
    _routines: Iterable[Routine]
    _list_label_references: ft.Ref[ft.Row]
    _terminal_reference: ft.Ref[ft.Container]
    _config: Config
    _current_filter: int | None

    def __init__(self, ):
        print("Initializing HomeView...")
        self._page = None
        self._current_filter = None
        self._terminal_reference = ft.Ref[ft.Container]()
        self._grid_reference = ft.Ref[ft.GridView]()
        self._list_label_references = ft.Ref[ft.Row]()
        self._config = Config()
        self._routines = []

    def _update_terminal(self, log: str) -> None:
        lv = self._terminal_reference.current.content
        if lv is None or not isinstance(lv, ft.ListView):
            return
        if len(lv.controls) >= self._TERMINAL_LIMIT:
            lv.controls.pop(0)
        lv.controls.append(ft.Text(log, style=ft.TextThemeStyle.LABEL_MEDIUM, selectable=True, color="#FFFFFF"))
        self._terminal_reference.current.update()

    def _teste(self):
        # sleep(5)
        last_length = 0
        while True:
            sleep(0.1)
            if len(self._config.log_capture.logs) != last_length and self._terminal_reference.current is not None:
                last_length = len(self._config.log_capture.logs)
                log = self._config.log_capture.get_log()
                self._update_terminal(log)

    def _mark_label_as_selected(self, category_id: int) -> None:
        for label in self._list_label_references.current.controls:
            if isinstance(label, CategoryLabels):
                label.set_selected(label.category.category_id == category_id and self._current_filter != category_id)

    def _filter_routines_by_category(self, category_id: int) -> None:
        self._mark_label_as_selected(category_id)
        if self._current_filter == category_id:
            self._current_filter = None
            self._grid_reference.current.controls = [
                RoutineCard(routine=routine)
                for routine in self._routines
            ]
        else:
            self._current_filter = category_id
            self._grid_reference.current.controls = [
                RoutineCard(routine=routine)
                for routine in self._routines
                if routine.category_id == category_id
            ]
        self._grid_reference.current.update()

    def set_page(self, page: ft.Page) -> None:
        self._page = page

    def get_view(self) -> ft.View:
        if self._page is None:
            raise ValueError("Page is not set for HomeView.")
        self._page.pubsub.subscribe(lambda m: self._update_terminal(m["text"]) if m.get("type")=="log" else None)
        Thread(target=self._teste, daemon=True).start()
        # Carga de dados com tratamento de erro para evitar travar a inicialização da página
        categories = []
        try:
            category_controller = CategoryController()
            categories = category_controller.get_all_categories()
        except Exception as e:
            logging.exception("Erro ao carregar categorias: %s", e)
            self._update_terminal(f"Erro ao carregar categorias: {e}")

        try:
            routines_controller = RoutinesController()
            self._routines = routines_controller.get_all_routines()
        except Exception as e:
            logging.exception("Erro ao carregar rotinas: %s", e)
            self._routines = []
            self._update_terminal(f"Erro ao carregar rotinas: {e}")
        home_view = ft.View(
            route="/home",
            controls=[
                ft.Container(
                    padding=ft.padding.all(20),
                    content=ft.Column(
                        controls=[
                            ft.Text("Categorias de Rotinas", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                            ft.Divider(),
                            ft.Container(
                                content=ft.ResponsiveRow(
                                    ref=self._list_label_references,
                                    expand=True,
                                    columns=12,
                                    spacing=10,
                                    run_spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    alignment=ft.MainAxisAlignment.START,
                                    controls=[
                                        CategoryLabels(
                                            category=category,
                                            width=100,
                                            col={"xs": 6, "md": 4, "lg": 2},
                                            on_click=lambda _, cat_id=category.category_id: self._filter_routines_by_category(cat_id)
                                        ) for category in categories
                                        
                                    ],
                                )
                            )
                        ]
                    )
                ),
                RoutinesGrid(
                    routines=self._routines,
                    ref=self._grid_reference
                ),
                ft.Container(
                    expand=True,
                    padding=ft.padding.all(20),
                    content=ft.Container(
                        padding=ft.padding.all(20),
                        ref=self._terminal_reference,
                        content=ft.ListView(
                            # height=100,
                            # scroll=ft.ScrollMode.AUTO,
                            auto_scroll=True,
                            # horizontal_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Divider(),
                                ft.Text("Bem vindo...", style=ft.TextThemeStyle.LABEL_MEDIUM, selectable=True, color="#FFFFFF"),
                            ],
                            spacing=10,
                        ),
                        alignment=ft.alignment.center,
                        bgcolor="#000000",
                        expand=True,
                        border_radius=5,
                    )
                )
            ],
            appbar=ft.AppBar(title=ft.Text(self._title)),
        )
        return home_view