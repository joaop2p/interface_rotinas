from typing import Optional, Sequence, Callable
from threading import Thread
from lib.src.services.routine_runner import RoutineRunner

class ScriptController:
    
    @staticmethod
    def run_script(
        script: str,
        args: Optional[Sequence[str]] = None,
        on_line: Optional[Callable[[str], None]] = None,
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
        background: bool = True,
    ) -> None:
        def worker():
            RoutineRunner().run(
                script_path=script,
                args=args,
                on_line=on_line,
                cwd=cwd,
                env=env,
            )
        if background:
            Thread(target=worker, daemon=True).start()
        else:
            worker()