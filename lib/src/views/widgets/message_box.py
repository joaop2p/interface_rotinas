import flet as ft

from lib.config import Config
from lib.src.controllers.script import ScriptController

class MessageBox(ft.AlertDialog):
    _script_controller: ScriptController = ScriptController()
    log = Config.get_instance().logger

    def _run(self, script: str) -> None:
        try:
            ScriptController.run_script(
                    script=script,
                    background=False,
                    # on_line=self.log.info, # type: ignore
                    on_line=lambda line: self.page.pubsub.send_all({"type": "log", "text": line}), # type: ignore
                )
        except Exception as e:
            self.log.error(f"Erro ao executar a rotina: '{e}'")
            snack_bar = ft.SnackBar(
                ft.Text(
                    f"Erro ao executar a rotina: '{e}'",
                    color=ft.Colors.WHITE
                ),
                bgcolor=ft.Colors.RED,
            )
            self.page.open(snack_bar)

    def __init__(self, title: str, dsc: str, script: str) -> None:
        super().__init__(
            title=ft.Text(
                'Deseja realmente executar a rotina: "',
                spans=[
                    ft.TextSpan(
                        text=title, style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                        ),
                    ft.TextSpan(text='"?'),
                    ],
                ),
            content=ft.Text(
                f"Essa rotina irá fazer: {dsc}"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self._close, style=ft.ButtonStyle(overlay_color=ft.Colors.RED_ACCENT, side=ft.BorderSide(color=ft.Colors.RED, width=1))),
                ft.TextButton("Executar", on_click=lambda e: (
                    self._close(e), 
                    self._run(script)
                ), style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True
        )

    def _close(self, e: ft.ControlEvent):
        self.open = False
        self.update()