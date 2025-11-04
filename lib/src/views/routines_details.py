import logging
from typing import Literal
from lib.src.models.db.models import Routine
from lib.src.views.widgets.datails_view import DetailsView
from lib.src.models.interfaces.view_template import ViewTemplate
from lib.src.controllers.category import CategoryController
from lib.src.controllers.routines import RoutinesController
from lib.config import AppConstants
import flet as ft

class RoutinesDetailsView(ViewTemplate):
    _title = "Detalhes da Rotina"
    _route = "/routine_details"
    _logger: logging.Logger
    _right_side_menu_ref: ft.Ref[ft.Container]
    _main_content_ref: ft.Ref[ft.Container]
    _routines_controller: RoutinesController
    
    def __init__(self):
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
        try:
            self._routines_controller = RoutinesController()
            self._routines = self._routines_controller.get_all_routines()
            self._logger.info(f"Rotinas carregadas: %d", len(self._routines))
        except Exception as e:
            self._logger.exception("Erro ao carregar rotinas: %s", e)
            self._routines = []

    def _on_save(self) -> None:
        """Salva as alterações da rotina com validação completa"""
        self._logger.info("Salvando alterações na rotina...")
        
        if not self._main_content_ref.current:
            self._show_error("Container principal não inicializado")
            return
        
        main_content = self._main_content_ref.current.content
        if not isinstance(main_content, DetailsView):
            self._show_error("Conteúdo principal inválido")
            return
        
        form_data = self._extract_form_data(main_content)
        if not form_data:
            return
        
        name, description, directory_path, category_id = form_data
        
        try:
            # Operação de salvamento
            self._routines_controller.update_routine(
                routine_id=main_content.routine.routine_id,
                name=name,
                description=description,
                directory_path=directory_path,
                category_id=category_id
            )
            
            self._show_success("Rotina atualizada com sucesso!")
            self._logger.info(f"Rotina '{name}' salva com sucesso")
            
            # Volta para modo visualização
            self._update_main_content(main_content.routine, mode="view")
            
        except Exception as e:
            error_msg = f"Erro ao salvar rotina: {e}"
            self._show_error(error_msg)
            self._logger.exception("Erro ao salvar rotina: %s", e)

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
                    on_click=lambda e: print(f"Arquivo selecionado no modo editar: {e}")
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

    def _go_back(self):
        if self._page is not None:
            self._page.go('/home')

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
                    on_click=lambda _: self._go_back()
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

    def _extract_form_data(self, details_view: DetailsView) -> tuple[str, str, str, int] | None:
        """Extrai e valida dados do formulário"""
        try:
            name = details_view.name_field.value
            description = details_view.description_field.value  
            directory_path = details_view.directory_path_field.value
            category_id = details_view.routine.category_id
            
            # Validação de campos obrigatórios
            if not name or not name.strip():
                self._show_error("Nome da rotina é obrigatório")
                return None
                
            if not description or not description.strip():
                self._show_error("Descrição da rotina é obrigatória")
                return None
                
            if not directory_path or not directory_path.strip():
                self._show_error("Caminho do diretório é obrigatório")
                return None
                
            if not category_id:
                self._show_error("Categoria é obrigatória")
                return None
            
            return name.strip(), description.strip(), directory_path.strip(), category_id
            
        except AttributeError as e:
            self._show_error("Erro ao acessar campos do formulário")
            self._logger.error(f"Erro de atributo ao extrair dados: {e}")
            return None

    def _show_error(self, message: str) -> None:
        """Mostra mensagem de erro ao usuário"""
        if self._page:
            snack_bar = ft.SnackBar(
                ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
            )
            self._page.open(snack_bar)
        self._logger.error(message)

    def _show_success(self, message: str) -> None:
        """Mostra mensagem de sucesso ao usuário"""
        if self._page:
            snack_bar = ft.SnackBar(
                ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN,
            )
            self._page.open(snack_bar)
        self._logger.info(message)

    def _validate_file_path(self, path: str) -> bool:
        """Valida se o caminho do arquivo existe e é válido"""
        import os
        
        if not os.path.exists(path):
            self._show_error(f"Arquivo não encontrado: {path}")
            return False
            
        if not path.endswith(tuple(AppConstants.PYTHON_EXTENSIONS)):
            self._show_error("Arquivo deve ser um script Python válido")
            return False
        
        return True