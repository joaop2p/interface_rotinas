import asyncio
import logging
from typing import Iterable
import flet as ft
from lib.src.controllers.routines import RoutinesController
from lib.src.controllers.category import CategoryController, Category
from lib.config import ConfigDefaults

class AddRoutinesView:
    _title = "Adicionar Rotina"
    _route = "/add_routine"
    _dropdown_ref: ft.Ref[ft.Dropdown]
    _categories: Iterable[Category]
    _label_selected_file_ref: ft.Ref[ft.Text]
    _selected_file: ft.FilePicker | None
    _name_field_ref: ft.Ref[ft.TextField]
    _description_field_ref: ft.Ref[ft.TextField]
    _category_selected: Category | None
    _category_index: dict[str, Category]

    def __init__(self):
        self._page = None
        self._dropdown_ref = ft.Ref[ft.Dropdown]()
        self._categories = []
        self._selected_file = None
        self._label_selected_file_ref = ft.Ref[ft.Text]()
        self._name_field_ref = ft.Ref[ft.TextField]()
        self._description_field_ref = ft.Ref[ft.TextField]()
        self._category_selected = None
        self._category_index = {}

    def set_page(self, page):
        self._page = page

    async def _load_data_async(self):
        try:
            category_controller = CategoryController()
            self._categories = category_controller.get_all_categories()
        except Exception as e:
            logging.exception("Erro ao carregar categorias: %s", e)

    @property
    def _get_category(self) -> None | Category:
        if self._dropdown_ref.current is None:
            logging.error("Dropdown não está inicializado.")
            return
        return self._category_index.get(self._dropdown_ref.current.value)

    async def _att_menu(self):
        # await asyncio.sleep(1)
        await self._load_data_async()
        if self._dropdown_ref.current is not None:
            self._category_index = {c.category_name: c for c in self._categories}
            self._dropdown_ref.current.options = [
                ft.DropdownOption(category.category_name, leading_icon=category.icon)
                for category in self._categories
            ]
            self._dropdown_ref.current.update()

    def _show_picker(self, e: ft.FilePickerResultEvent):
        if e.files:
            self._selected_file = e.files[0]
            logging.info(f"Arquivo selecionado: {self._selected_file.path}")
            label = self._label_selected_file_ref.current
            if label is not None:
                label.value = f"Script selecionado: {self._selected_file.name}"
                label.update()

    def _reset_form(self):
        self._name_field_ref.current.value = ""
        self._name_field_ref.current.error_text = None
        self._name_field_ref.current.update()
        self._description_field_ref.current.value = ""
        self._description_field_ref.current.error_text = None
        self._description_field_ref.current.update()
        if self._dropdown_ref.current is not None:
            self._dropdown_ref.current.value = None
            self._dropdown_ref.current.update()
        self._selected_file = None
        label = self._label_selected_file_ref.current
        if label is not None:
            label.value = "Script selecionado: Nenhum"
            label.update()

    def _validate_inputs(self) -> bool:
        fields = [self._name_field_ref, self._description_field_ref]
        for field in fields:
            if field.current is None or not field.current.value.strip():
                if field.current is not None:
                    field.current.error_text = "Este campo não pode estar vazio."
                    field.current.update()
                    return False
        if self._dropdown_ref.current is None or self._dropdown_ref.current.value is None:
            snack_bar = ft.SnackBar(
                ft.Text(
                    "Por favor, selecione uma categoria para a rotina.",
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.RED,
            )
            self._page.open(snack_bar)
            return False
        elif self._selected_file is None:
            snack_bar = ft.SnackBar(
                ft.Text(
                    "Por favor, selecione um script python para a rotina.",
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.RED,
            )
            self._page.open(snack_bar)
            return False
        return True
    
    def _save_routine(self) -> None:
        if not self._validate_inputs():
            return
        # Lógica para salvar a rotina
        try:
            logging.info("Salvando rotina:")
            logging.info(f"Nome: {self._name_field_ref.current.value}")
            logging.info(f"Descrição: {self._description_field_ref.current.value}")
            logging.info(f"Categoria: {self._dropdown_ref.current.value}")
            logging.info(f"Script: {self._selected_file.path}")
            routine_controller = RoutinesController()
            routine_controller.insert_routine(
                name=self._name_field_ref.current.value,
                desc=self._description_field_ref.current.value,
                category_id=self._get_category.category_id,
                path=self._selected_file.path
            )
            snack_bar = ft.SnackBar(
            ft.Text(
                "Rotina adicionada com sucesso!",
                color=ft.Colors.WHITE
            ),
            bgcolor=ft.Colors.GREEN,
        )
        except Exception as e:
            snack_bar = ft.SnackBar(
                ft.Text(
                    f"Erro ao adicionar rotina: {e}",
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.RED,
            )
            logging.exception("Erro ao adicionar rotina: %s", e)
            self._page.open(snack_bar)
            return
        
        self._page.open(snack_bar)
        self._reset_form()

    def get_view(self):
        if self._page is None:
            raise ValueError("Page is not set for AddRoutineView.")
        self._page.run_task(self._att_menu)
        picker = ft.FilePicker(on_result=self._show_picker)
        self._page.overlay.append(picker)
        return ft.View(
            route=self._route,
            controls=[
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("Aqui você pode adicionar uma nova rotina."),
                            ft.Divider(),
                            ft.TextField(label="Nome da Rotina", width=300, ref=self._name_field_ref),
                            ft.TextField(label="Descrição", width=300, multiline=True, ref=self._description_field_ref),
                            ft.Dropdown(
                                label="Categoria",
                                width=300,
                                ref=self._dropdown_ref,
                            ),
                            ft.Row(
                                controls=[
                                    ft.OutlinedButton(
                                        "Selecionar script python", 
                                        icon=ft.Icons.ATTACH_FILE,
                                        on_click=lambda e: picker.pick_files(
                                            allow_multiple=False,
                                            allowed_extensions=ConfigDefaults.EXTENSION_SUPPORTED,
                                            dialog_title=ConfigDefaults.WINDOW_TITLE
                                        )
                                    ),
                                    ft.Text("Script selecionado: Nenhum", ref=self._label_selected_file_ref),
                                ]
                            ),

                            ft.ElevatedButton("Salvar Rotina", on_click=lambda e: self._save_routine())
                        ]
                    )
                )
                # Add more controls as needed
            ],
            appbar=ft.AppBar(
                title=ft.Text(self._title),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: self._page.go("/home")
                )
            )
        )