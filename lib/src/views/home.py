import asyncio
import logging
from typing import Iterable
from lib.config import Config, ConfigDefaults
from lib.src.controllers.routines import RoutinesController
from lib.src.controllers.category import CategoryController, CategoryInUseError
from lib.src.models.db.models import Category, Routine
from lib.src.models.interfaces.view_template import ViewTemplate
import flet as ft
from lib.src.views.widgets.category_labels import CategoryLabels
from lib.src.views.widgets.routines_grid import RoutineCard, RoutinesGrid

class HomeView(ViewTemplate):
    _title = "Menu Inicial"
    _route = "/home"
    _routines: Iterable[Routine]
    _categories: Iterable[Category]
    _config: Config
    _current_filter: int | None
    _load_task: asyncio.Task | None
    _grid_ref: ft.Ref[ft.GridView]
    _list_label_ref: ft.Ref[ft.Container]
    _terminal_ref: ft.Ref[ft.Container]
    _main_content_ref: ft.Ref[ft.Container]
    _monitor_logs_task: asyncio.Task | None
    _logger: logging.Logger

    def __init__(self, ):
        self._current_filter = None
        self._config = Config()
        self._logger = logging.getLogger("HomeView")
        self._load_task = None
        self._routines = []
        self._categories = []
        self._start_references()
        self._monitor_logs_task = None
        
    
    def _start_references(self) -> None:
        self._terminal_reference = ft.Ref[ft.Container]()
        self._grid_reference = ft.Ref[ft.GridView]()
        self._list_label_references = ft.Ref[ft.Container]()
        self._main_content_ref = ft.Ref[ft.Container]()

    def _update_terminal(self, log: str) -> None:
        lv = self._terminal_reference.current.content
        if lv is None or not isinstance(lv, ft.ListView):
            return
        if len(lv.controls) >= ConfigDefaults.TERMINAL_LIMIT:
            lv.controls.pop(0)
        lv.controls.append(ft.Text(log, style=ft.TextThemeStyle.LABEL_MEDIUM, selectable=True, color="#FFFFFF"))
        self._terminal_reference.current.update()

    def _on_delete_category(self, category: Category) -> None:
        try:
            category_controller = CategoryController()
            category_controller.delete_category(category)
            self._logger.info(f"Categoria deletada: {category.category_name} (ID: {category.category_id})")
            # self._update_terminal(f"Categoria deletada: {category.category_name} (ID: {category.category_id})")
            self._page.run_task(self._switch_to_main_content)
        except CategoryInUseError as e:
            self._logger.warning("Tentativa de deletar categoria em uso: %s", e)
            self._update_terminal(f"Erro ao deletar categoria: {e}")
        except Exception as e:
            self._logger.exception("Erro ao deletar categoria: %s", e)
            # self._update_terminal(f"Erro ao deletar categoria: {e}")

    async def _monitor_logs(self):
        last_length = 0
        while True:
            await asyncio.sleep(ConfigDefaults.TERMINAL_UPDATE_INTERVAL)
            if len(self._config.log_capture.logs) != last_length and self._terminal_reference.current is not None:
                last_length = len(self._config.log_capture.logs)
                log = self._config.log_capture.get_log()
                self._update_terminal(log)

    def _mark_label_as_selected(self, category_id: int) -> None:
        for label in self._list_label_references.current.content.controls:
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
                for routine in self._routines if routine.category_id == category_id
            ]
        self._grid_reference.current.update()

    async def _load_data_async(self):
        try:
            category_controller = CategoryController()
            self._categories = category_controller.get_all_categories()
            self._logger.info(f"Categorias carregadas: %d", len(self._categories))
        except Exception as e:
            self._logger.exception("Erro ao carregar categorias: %s", e)
            self._update_terminal(f"Erro ao carregar categorias: {e}")
        try:
            routines_controller = RoutinesController()
            self._routines = routines_controller.get_all_routines()
            self._logger.info(f"Rotinas carregadas: %d", len(self._routines))
        except Exception as e:
            self._logger.exception("Erro ao carregar rotinas: %s", e)
            self._routines = []
            self._update_terminal(f"Erro ao carregar rotinas: {e}")

    def _get_categories_menu(self):
        if not self._categories:
            return ft.Text("Nenhuma categoria disponível", style=ft.TextThemeStyle.LABEL_MEDIUM)
        return ft.ResponsiveRow(
            expand=True,
            columns=12,
            spacing=10,
            run_spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.START,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                CategoryLabels(
                    category=category,
                    on_click=lambda e, c=category: self._filter_routines_by_category(c.category_id),
                    width=100,
                    col={"xs": 6, "md": 4, "lg": 2},
                    on_delete=lambda e, c=category: self._on_delete_category(c),
                ) for category in self._categories
            ],
        )

    def _get_routines_grid(self):
        if not self._routines:
            return ft.Container(
                content=ft.Text("Nenhuma rotina disponível", style=ft.TextThemeStyle.LABEL_MEDIUM),
                alignment=ft.alignment.center,
            )
        return RoutinesGrid(
            routines=self._routines,
            ref=self._grid_reference
        )

    async def _switch_to_main_content(self):
        await self._load_data_async()
        self._list_label_references.current.content = self._get_categories_menu()
        self._main_content_ref.current.content = self._get_routines_grid()
        self._list_label_references.current.update()
        self._main_content_ref.current.update()

    def _go_to(self, route: str) -> None:
        if self._monitor_logs_task is not None:
            self._monitor_logs_task.cancel()
        if self._page is not None:
            self._page.go(route)

    def set_page(self, page: ft.Page) -> None:
        self._page = page

    def get_view(self) -> ft.View:
        if self._page is None:
            raise ValueError("Page is not set for HomeView.")
        self._page.run_task(self._switch_to_main_content)
        self._page.pubsub.subscribe(lambda m: self._update_terminal(m["text"]) if m.get("type")=="log" else None)
        self._monitor_logs_task = self._page.run_task(self._monitor_logs)
        home_view = ft.View(
            route="/home",
            controls=[
                ft.Container(
                    padding=ft.padding.all(20),
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(self._title, style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                                    ft.PopupMenuButton(
                                        icon=ft.Icons.ADD,
                                        items=[
                                            ft.PopupMenuItem(
                                                text="Adicionar Categoria",
                                                icon=ft.Icons.NEW_LABEL,
                                                on_click=lambda e: self._go_to("/add_category")
                                            ),
                                            ft.PopupMenuItem(
                                                text="Adicionar Rotina",
                                                icon=ft.Icons.PLAYLIST_ADD,
                                                on_click=lambda e: self._go_to("/add_routine")
                                            ),
                                            ft.PopupMenuItem(
                                                text="Detalhes das Rotinas",
                                                icon=ft.Icons.INFO,
                                                on_click=lambda e: self._go_to("/routine_details")
                                            )
                                        ]
                                    )
                                ]
                            ),
                            ft.Divider(),
                            ft.Container(
                                ref=self._list_label_references,
                                content=ft.ProgressRing(),
                            )
                        ]
                    )
                ),
                ft.Container(
                    ref=self._main_content_ref,
                    content=ft.Container(
                        ft.ProgressRing(),
                        alignment=ft.alignment.center,
                    ),
                    expand=True,
                ),
                ft.Container(
                    expand=True,
                    padding=ft.padding.all(20),
                    content=ft.Container(
                        padding=ft.padding.all(20),
                        ref=self._terminal_reference,
                        content=ft.ListView(
                            auto_scroll=True,
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
        )
        return home_view