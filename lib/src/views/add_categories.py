import logging
from lib.src.controllers.category import CategoryController
from lib.src.models.interfaces.view_template import ViewTemplate
from lib.src.views.widgets.icon_selector import IconSelector
import flet as ft

class AddCategoriesView(ViewTemplate):
    _title = "Adicionar Categoria"
    _route = "/add_category"
    _icon: str | None
    _selected_icon_text_ref: ft.Ref[ft.Text]
    _text_field_ref: ft.Ref[ft.TextField]

    def __init__(self):
        self._page = None
        self._icon = None
        self._selected_icon_text_ref = ft.Ref[ft.Text]()
        self._text_field_ref = ft.Ref[ft.TextField]()

    def set_page(self, page):
        self._page = page

    def _on_icon_selected(self, icon_name: str | None):
        label = self._selected_icon_text_ref.current
        if label is not None:
            label.value = f"Ícone selecionado: {icon_name or 'Nenhum'}"
            self._icon = icon_name
            label.update()

    def _validate_inputs(self) -> bool:
        name_field = self._text_field_ref.current
        selected_icon = self._selected_icon_text_ref.current
        if name_field is None or not name_field.value.strip():
            if name_field is not None:
                name_field.error_text = "O nome da categoria não pode estar vazio."
                name_field.update()
            return False
        elif self._icon is None:
            snack_bar = ft.SnackBar(
                ft.Text(
                    "Por favor, selecione um ícone para a categoria.",
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.RED,
            )
            self._page.open(snack_bar)
            return False
        return True
    
    def _save_category(self) -> None:
        if not self._validate_inputs():
            return
        category_controller = CategoryController()
        try:
            category_controller.insert_category(
                name=self._text_field_ref.current.value,
                icon=self._icon.value
            )
            snack_bar = ft.SnackBar(
                ft.Text(
                    "Categoria adicionada com sucesso!",
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.GREEN,
            )
        except Exception as e:
            snack_bar = ft.SnackBar(
                ft.Text(
                    f"Erro ao adicionar categoria: {e}",
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.RED,
            )
            logging.exception("Erro ao adicionar categoria: %s", e)
        self._page.open(snack_bar)

    def get_view(self) -> ft.View:
        if self._page is None:
            raise ValueError("Page not set for AddCategoriesView")
        return ft.View(
            route=self._route,
            controls=[
                ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Aqui você pode adicionar uma nova categoria.", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                        ft.TextField(
                            label="Nome da Categoria", 
                            width=300,
                            ref=self._text_field_ref
                        ),
                        ft.OutlinedButton(
                            "Selecionar Ícone",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: self._page.open(
                                IconSelector(on_accept=self._on_icon_selected)
                            ),
                        ),
                        ft.Text(ref=self._selected_icon_text_ref, value="Ícone selecionado: Nenhum"),
                        ft.ElevatedButton("Salvar Categoria", on_click=lambda e: self._save_category())
                        ]
                    ),
                    padding=20
                ),
            ],
            appbar=ft.AppBar(
                title=ft.Text(self._title),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: self._page.go("/home")
                )
            )
        )