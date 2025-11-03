import logging
from typing import Literal
from lib.src.models.db.models import Routine
from lib.src.views.widgets.datails_view import DetailsView
from lib.src.models.interfaces.view_template import ViewTemplate
from lib.src.controllers.category import CategoryController
from lib.src.controllers.routines import RoutinesController
import flet as ft

class RoutinesDetailsView(ViewTemplate):
    _title = "Detalhes da Rotina"
    _route = "/routine_details"
    _logger: logging.Logger
    _right_side_menu_ref: ft.Ref[ft.Container]
    _main_content_ref: ft.Ref[ft.Container]
    _routines_controller: RoutinesController
    
    def __init__(self):
        self._page = None
        self._logger = logging.getLogger("RoutinesDetailsView")
        self._right_side_menu_ref = ft.Ref[ft.Container]()
        self._main_content_ref = ft.Ref[ft.Container]()

    def _search_routines(self, query: str):
        filtered = [
            routine for routine in self._routines
            if query.lower() in routine.routine_name.lower()
        ]
        self._right_side_menu_ref.current.content = ft.ListView(
            controls=[
                ft.Dismissible(
                    ft.Card(
                        ft.ListTile(
                            leading=ft.Icon(routine.category.icon),
                            title=ft.Text(
                                routine.routine_name
                            ),
                            subtitle=ft.Text(
                                f"Categoria: {next((cat.category_name for cat in self._categories if cat.category_id == routine.category_id), 'N/A')}"
                            ),
                            trailing=ft.Icon(ft.Icons.MORE_VERT)
                        )
                    )
                )
                for routine in filtered
            ]
        )
        self._logger.info(f"Rotinas filtradas: {len(filtered)} para a consulta '{query}'")
        self._right_side_menu_ref.current.update()
        return filtered

    async def _load_data_async(self):
        try:
            category_controller = CategoryController()
            self._categories = category_controller.get_all_categories()
            self._logger.info(f"Categorias carregadas: %d", len(self._categories))
        except Exception as e:
            self._logger.exception("Erro ao carregar categorias: %s", e)
            self._update_terminal(f"Erro ao carregar categorias: {e}")
        try:
            self._routines_controller = RoutinesController()
            self._routines = self._routines_controller.get_all_routines()
            self._logger.info(f"Rotinas carregadas: %d", len(self._routines))
        except Exception as e:
            self._logger.exception("Erro ao carregar rotinas: %s", e)
            self._routines = []
            self._update_terminal(f"Erro ao carregar rotinas: {e}")

    def _on_save(self):
        self._logger.info("Salvando alterações na rotina...")
        if self._main_content_ref.current is None:
            self._logger.error("Main content container não está inicializado.")
            return
        
        self._routines_controller.insert_routine(
            name=self._main_content_ref.current.content._name_field_ref.current.value,
            desc=self._main_content_ref.current.content._description_field_ref.current.value,
            directory_path=self._main_content_ref.current.content._directory_path_field_ref.current.value,
            category_id=self._main_content_ref.current.content._routine.category_id,
        )

    def _update_main_content(self, routine: Routine, mode: Literal["view", "edit"] = "view"):
        match mode:
            case "view":
                if self._main_content_ref.current is None:
                    self._logger.error("Main content container não está inicializado.")
                    return
                print("Atualizando main content para modo view")
                self._main_content_ref.current.content = DetailsView(routine=routine)
                # self._main_content_ref.current.update()
            case "edit":
                if self._main_content_ref.current is None:
                    self._logger.error("Main content container não está inicializado.")
                    return
                details_view = DetailsView(
                    routine=routine, 
                    mode="edit", 
                    on_pick=lambda e: print(f"Arquivo selecionado no modo editar: {e}")
                )
                self._main_content_ref.current.content = details_view
                details_view.set_page(self._page)
                details_view.unlock_fields()
        if self._main_content_ref.current is None:
            self._logger.error("Main content container não está inicializado.")
            return
        self._main_content_ref.current.update()

    async def _switch_to_main_content(self):
        await self._load_data_async()
        if self._right_side_menu_ref.current is None:
            self._logger.error("Main content container não está inicializado.")
            return
        self._right_side_menu_ref.current.content = ft.ListView(
            controls=[
                ft.Dismissible(
                    ft.Card(
                        ft.ListTile(
                            leading=ft.Icon(routine.category.icon),
                            title=ft.Text(
                                routine.routine_name
                            ),
                            subtitle=ft.Text(
                                f"Categoria: {next((cat.category_name for cat in self._categories if cat.category_id == routine.category_id), 'N/A')}"
                            ),
                            trailing=ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        text="Editar",
                                        on_click=lambda _, r=routine: self._update_main_content(r, mode="edit")
                                    ),
                                    # ft.PopupMenuItem(
                                    #     text="Deletar",
                                    #     on_click=lambda _, r=routine: self._delete_routine(r)
                                    # )
                                ]
                            ),
                            on_click=lambda _, r=routine: self._update_main_content(r)
                        )
                    )
                )
                for routine in self._routines
            ]
        )
        self._right_side_menu_ref.current.update()
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
                    padding=20,
                    expand=True,
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Container(
                                            content=ft.TextField(
                                                hint_text="Pesquisar rotina...",
                                                width=400,
                                                on_change=lambda e: self._search_routines(e.control.value)
                                            )
                                        ),
                                        ft.Container(
                                            ref=self._right_side_menu_ref,
                                            width=400,
                                            padding=20,
                                            # bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                                            content=ft.Container(
                                                alignment=ft.alignment.center,
                                                content=ft.ProgressRing()
                                            ),
                                            expand=True,
                                            )
                                    ]
                                ),
                            ),
                            ft.Container(
                                content=ft.VerticalDivider()
                            ),
                            ft.Container(
                                expand=True,
                                alignment=ft.alignment.top_center,
                                ref=self._main_content_ref,
                                content=DetailsView(
                                    # width=400,
                                    padding=20,
                                    margin=ft.margin.only(left=20),
                                    content=ft.Text("Detalhes da rotina serão exibidos aqui.")
                                )
                            )
                            
                        ]
                    ),
                ),
            ]
        )