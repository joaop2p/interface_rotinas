from typing import Self
import logging
from logging import Logger, Handler, LogRecord
import sys
import threading
from collections import deque
from . import AppConstants

class InMemoryLogHandler(Handler):
    def __init__(self, max_logs: int = 1000) -> None:
        super().__init__()
        self.logs: deque[str] = deque(maxlen=max_logs)
        self.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    def emit(self, record: LogRecord) -> None:
        try:
            self.logs.append(self.format(record))
        except Exception:
            self.handleError(record)

    def get_all_logs(self) -> str:
        return "\n".join(self.logs)

    def get_log(self) -> str:
        return self.logs[-1] if self.logs else ""
    
    def get_recent_logs(self, count: int = 50) -> list[str]:
        """Retorna os N logs mais recentes"""
        return list(self.logs)[-count:]

    def clear_logs(self) -> None:
        """Limpa todos os logs"""
        self.logs.clear()

class LoggerConfig:
    logger: Logger
    log_capture: InMemoryLogHandler
    _instance: Self | None = None
    _initialized: bool = False
    _lock = threading.Lock()

    def __new__(cls) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LoggerConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self, max_logs: int = AppConstants.MAX_LOG_LINES, log_level: int = logging.INFO) -> None:
        self.log_capture = InMemoryLogHandler(max_logs)
        self._setup_root_logger(log_level)
    
    def _setup_root_logger(self, log_level: int) -> None:
        root = logging.getLogger()
        root.setLevel(log_level)
        root.handlers.clear()
        root.addHandler(self.log_capture)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("%(levelname)s - %(name)s - %(message)s")
        )
        root.addHandler(console_handler)
        self.logger = root

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_child_logger(self, name: str) -> Logger:
        """Cria um logger filho com nome específico"""
        return self.logger.getChild(name)

    def set_log_level(self, level: int) -> None:
        """Altera o nível de log dinamicamente"""
        logging.getLogger().setLevel(level)
        self.logger.setLevel(level)

    def get_logs_for_terminal(self, count: int = 100) -> list[str]:
        """Retorna logs formatados para exibição no terminal"""
        return self.log_capture.get_recent_logs(count)