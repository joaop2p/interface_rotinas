import logging
from lib.src.models.interfaces.view_template import ViewTemplate
from lib.src.controllers.category import CategoryController
from lib.src.controllers.routines import RoutinesController
import flet as ft

class RoutinesDetailsView(ViewTemplate):
    _title = "Detalhes da Rotina"
    _route = "/routine_details"
    _logger: logging.Logger
    _main_content_ref: ft.Ref[ft.Container]
    
    def __init__(self):
        self._page = None
        self._logger = logging.getLogger("RoutinesDetailsView")
        self._main_content_ref = ft.Ref[ft.Container]()

    async def _load_data_async(self):
        try:
            category_controller = CategoryController()
            self._categories = category_controller.get_all_categories()
            self._logger.info(f"Categorias carregadas: %d", len(self._categories))
        except Exception as e:
            self._logger.exception("Erro ao carregar categorias: %s", e)
            # self._update_terminal(f"Erro ao carregar categorias: {e}")
        try:
            routines_controller = RoutinesController()
            self._routines = routines_controller.get_all_routines()
            self._logger.info(f"Rotinas carregadas: %d", len(self._routines))
        except Exception as e:
            self._logger.exception("Erro ao carregar rotinas: %s", e)
            self._routines = []
            # self._update_terminal(f"Erro ao carregar rotinas: {e}")

    async def _switch_to_main_content(self):
        await self._load_data_async()
        self._main_content_ref.current.content = ft.ListView(
            [ft.Dismissible(ft.ListTile(title=ft.Text(routine.routine_name))) for routine in self._routines]
        )
        self._main_content_ref.current.update()
        #TODO: Implementar deletar rotinas a partir do Dismissible

    def set_page(self, page):
        self._page = page

    def get_view(self):
        if self._page is None:
            raise ValueError("Page not set for RoutinesDetailsView")
        self._page.run_task(self._switch_to_main_content)
        return ft.View(
            route=self._route,
            appbar=ft.AppBar(
                title=ft.Text(self._title),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: self._page.go("/home")
                )
            ),
            controls=[
                ft.Container(
                    ref=self._main_content_ref,
                    content=ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.ProgressRing()
                    ),
                    expand=True,
                    )
            ]
        )