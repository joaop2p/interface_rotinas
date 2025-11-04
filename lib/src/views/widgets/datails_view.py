from typing import Literal, Optional, Callable
import flet as ft
from os.path import isfile, exists
from lib.src.models.db.models import Routine
from lib.config import AppConstants

class DetailsView(ft.Container):
    _name_field_ref: ft.Ref[ft.TextField]
    _description_field_ref: ft.Ref[ft.TextField]
    _directory_path_field_ref: ft.Ref[ft.TextField]
    _save_button_ref: ft.Ref[ft.Container]
    _select_file_ref: ft.Ref[ft.IconButton]
    _routine: Routine
    _state: Literal["view", "edit"] = "view"
    _file_picker: ft.FilePicker
    _page: Optional[ft.Page]

    def __init__(self, routine: Optional[Routine] = None, mode: Literal["view", "edit"] = "view", on_save: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self._state = mode
        self._page = None
        self._on_save = on_save

        # Cria o file picker com callback
        self._file_picker = ft.FilePicker(
            on_result=lambda e: self._on_file_selected(e)
        )
        
        if routine is None:
            self.content = ft.Text("Nenhuma rotina para ser exibida.", theme_style=ft.TextThemeStyle.BODY_MEDIUM)
        else:
            self._routine = routine
            self.content = self._build_content()

    def _set_directory_path(self, path: str):
        self._directory_path_field_ref.current.value = path
        self._directory_path_field_ref.current.update()

    def set_page(self, page: ft.Page):
        """Define a página e adiciona o file picker aos overlays"""
        self._page = page
        if self._file_picker not in page.overlay:
            page.overlay.append(self._file_picker)
            page.update()

    def _on_file_selected(self, e: ft.FilePickerResultEvent):
        """Callback chamado quando um arquivo é selecionado"""
        if e.files and len(e.files) > 0:
            selected_file = e.files[0]
            if self._directory_path_field_ref.current:
                self._directory_path_field_ref.current.value = selected_file.path
                self._directory_path_field_ref.current.update()
                # Validar o arquivo selecionado
                self._check_path_exists_direct(selected_file.path)

    def _init_fields(self):
        self._name_field_ref = ft.Ref[ft.TextField]()
        self._description_field_ref = ft.Ref[ft.TextField]()
        self._directory_path_field_ref = ft.Ref[ft.TextField]()
        self._save_button_ref = ft.Ref[ft.Container]()
        self._select_file_ref = ft.Ref[ft.IconButton]()

    def unlock_fields(self):
        self._state = "edit"
        fields = [
            self._name_field_ref,
            self._description_field_ref,
            self._directory_path_field_ref]
        for field in fields:
            if field.current:
                field.current.read_only = False
        self._select_file_ref.current.visible = True
        self._save_button_ref.current.visible = True

    def _validate_inputs(self) -> bool:
        fields = [
            self._name_field_ref, self._description_field_ref, self._directory_path_field_ref
            ]
        for field in fields:
            if field.current.value is None or not field.current.value.strip():
                field.current.error_text = "Este campo não pode estar vazio."
                field.current.update()
                return False
        return True

    def _check_path_exists(self, e: ft.ControlEvent):
        """Validação de caminho via evento de mudança no campo"""
        self._check_path_exists_direct(e.control.value)
        e.control.update()

    def _check_path_exists_direct(self, path: str):
        """Validação direta de caminho (usado tanto no evento quanto no picker)"""
        field = self._directory_path_field_ref.current
        if not field:
            return
            
        print(f"Verificando existência do caminho: {path}")
        if exists(path):
            if isfile(path):
                field.error_text = None
            else:
                field.error_text = "O caminho não é um arquivo válido."
        else:
            field.error_text = "Caminho não encontrado."

    def _open_file_picker(self, e):
        """Abre o file picker com as configurações adequadas"""
        if self._file_picker:
            self._file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=AppConstants.PYTHON_EXTENSIONS,
                dialog_title=AppConstants.FILE_PICKER_TITLE
            )

    def _build_content(self):
        self._init_fields()
        return ft.Column(
            controls=[
                ft.ResponsiveRow(
                    columns=12,
                    spacing=10,
                    controls=[
                        ft.TextField(
                            ref=self._name_field_ref,
                            label="Nome da Rotina",
                            value=self._routine.routine_name,
                            read_only=True,
                            expand=True,
                            col={"xs": 10, "md": 8, "lg": 4}
                        ),
                        ft.TextField(
                            ref=self._description_field_ref,
                            label="Descrição",
                            value=self._routine.description or "",
                            read_only=True,
                            expand=True,
                            multiline=True,
                            col={"xs": 10, "md": 8, "lg": 4}
                        ),
                        ft.Container(
                            col={"xs": 10, "md": 8, "lg": 4},
                            content=ft.Row(
                                controls=[
                                    ft.TextField(
                                        ref=self._directory_path_field_ref,
                                        label="Caminho do Diretório",
                                        value=self._routine.directory_path,
                                        on_change=self._check_path_exists,
                                        read_only=True,
                                        expand=True,
                                    ),
                                    ft.IconButton(
                                        visible=False,
                                        ref=self._select_file_ref,
                                        icon=ft.Icons.ATTACH_FILE,
                                        tooltip="Selecionar arquivo",
                                        on_click=self._open_file_picker
                                    ),
                                ]
                            )
                        ),
                        #TODO: adicionar campo categoria
                        ft.Text(
                            f"Data de Criação: {self._routine.dt_created.strftime('%d/%m/%Y %H:%M:%S')}",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM
                        ),
                        ft.Text(
                            f"Data de Modificação: {self._routine.dt_modified.strftime('%d/%m/%Y %H:%M:%S')}",
                            theme_style=ft.TextThemeStyle.BODY_MEDIUM
                        ),
                    ]
                ),
                ft.Container(
                    height=20,
                    content=ft.Divider()
                ),
                ft.Container(
                    ref=self._save_button_ref,
                    alignment=ft.alignment.center,
                    visible=self._state == "edit",
                    content=ft.IconButton(
                        icon=ft.Icons.SAVE,
                        tooltip="Salvar",
                        on_click=lambda _: (self._validate_inputs(), self._on_save() if self._on_save else None)
                    )
                )
            ]
        )