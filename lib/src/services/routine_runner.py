import sys
import subprocess
import os
from typing import Callable, Sequence, Optional
from lib.config.settings import Config

class RoutineRunner:
    def __init__(self) -> None:
        self._logger = Config.get_instance().logger

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
        if args is None:
            args = []

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
        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip("\n")
            if on_line:
                on_line(line)
            else:
                # encaminha para o logger do app -> capturado em memória
                self._logger.info(line)

        proc.stdout.close()
        rc = proc.wait()
        end_msg = f"[rotina terminou com código {rc}]"
        if on_line:
            on_line(end_msg)
        else:
            self._logger.info(end_msg)
        return rc