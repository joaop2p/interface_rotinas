import sys
import subprocess
import os
from re import compile
from typing import Callable, Sequence, Optional
from lib.config import get_logger

class RoutineRunner:
    def __init__(self) -> None:
        self._logger = get_logger("RoutineRunner")
        self._progress_pattern = compile(r'\d+(?:\.\d+)?%')

    def run(
        self,
        script_path: str,
        args: Optional[Sequence[str]] = None,
        on_line: Optional[Callable[[str], None]] = None,
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
        hide_console: bool = True,
    ) -> int:
        """
        Executa um script Python em um novo processo e captura a saída em tempo real.
        """
        name = os.path.basename(script_path)
        self._logger.info(f"Iniciando rotina: {name}")
        if not os.path.isfile(script_path):
            raise FileNotFoundError(f"Script não encontrado: {script_path}")
        if args is None:
            args = []
        if cwd is None:
            cwd = os.path.dirname(os.path.abspath(script_path))

        python_exe = sys.executable  # usa o mesmo interpretador do app
        cmd = [python_exe, "-u", script_path, *args]  # -u: unbuffered

        creationflags = 0
        if os.name == "nt" and hide_console:
            creationflags = subprocess.CREATE_NO_WINDOW  # evita abrir console no Windows

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            env=env,
            bufsize=1,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
        )

        assert proc.stdout is not None
        is_progress_mode = False
        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip("\n\r")
            if bool(self._progress_pattern.search(line)):
                if on_line:
                    on_line(f"\r{line}")
                is_progress_mode = True
            else:
                if is_progress_mode:
                    if on_line:
                        on_line("")  # Quebra de linha ao sair do modo progresso
                    is_progress_mode = False
                
                if on_line:
                    on_line(line)
                else:
                    self._logger.info(line)

        if is_progress_mode and on_line:
            on_line("")
        proc.stdout.close()
        rc = proc.wait()
        end_msg = f"[rotina {name} terminou com código: {rc}]"
        if on_line:
            on_line(end_msg)
        else:
            self._logger.info(end_msg)
        return rc