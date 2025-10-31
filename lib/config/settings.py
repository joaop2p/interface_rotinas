from typing import Self
import logging
from logging import Logger, Handler, LogRecord
import sys

class InMemoryLogHandler(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.logs: list[str] = []
        self.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    def emit(self, record: LogRecord) -> None:
        try:
            self.logs.append(self.format(record))
        except Exception:
            pass

    def get_all_logs(self) -> str:
        return "\n".join(self.logs)

    def get_log(self) -> str:
        return self.logs[-1] if self.logs else ""

class Config:
    logger: Logger
    log_capture: InMemoryLogHandler
    _instance: Self | None = None
    _initialized: bool = False

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self.__class__._initialized:
            return
        self.log_capture = InMemoryLogHandler()

        root = logging.getLogger()
        root.setLevel(logging.INFO)
        # Evita handlers duplicados
        existing = {type(h) for h in root.handlers}
        if InMemoryLogHandler not in existing:
            root.addHandler(self.log_capture)
        if logging.StreamHandler not in existing:
            root.addHandler(logging.StreamHandler(sys.__stdout__))

        self.logger = logging.getLogger("app")
        self.logger.propagate = True

        self.__class__._initialized = True

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance