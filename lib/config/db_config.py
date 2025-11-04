import logging
from os.path import exists
import threading
from sqlalchemy import Engine, create_engine, event
from contextlib import contextmanager
from sqlmodel import SQLModel, Session
from . import AppConstants, LogMessages, SQLConstants
from typing import Self, Any
from ..src.models.db.models import *

class DatabaseConfig:
    _instance = None
    _initialized = False
    _lock = threading.Lock()

    def __init__(self, echo: bool = False) -> None:
        """Inicializa o engine de banco de dados como singleton com opções de pool.

        - Usa SQLite por padrão (com base em CONFIG.database).
        - Ativa pool_pre_ping para detectar conexões quebradas.
        - Para bancos não-SQLite, permite configurar pool_size, max_overflow e pool_recycle via env vars.
        - Cria o schema (SQLModel.metadata.create_all) na primeira inicialização.
        """
        if self.__class__._initialized:
            return
        self.logger = logging.getLogger("DatabaseConfig")
        self.logger.debug("Inicializando DatabaseConfig...")
    
        path = AppConstants.get_database_path()
        new = not exists(path)
        url = f"sqlite:///{path}"
        try:
            self.logger.info(LogMessages.format_safe(LogMessages.DB_CONNECTING, db_path=url))
    
            # SQLite apenas - aplicação desktop local
            engine_kwargs: dict[str, Any] = {
                "echo": echo,
                "future": True,
                "pool_pre_ping": True,
                "connect_args": {"check_same_thread": False}
            }

            self.engine: Engine = create_engine(url, **engine_kwargs)
            SQLModel.metadata.create_all(self.engine)

            # Configuração específica do SQLite
            @event.listens_for(self.engine, "connect")
            def _configure_sqlite(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute(SQLConstants.ACTIVE_FOREIGN_KEYS)
                cursor.execute(SQLConstants.TRIGGER_UPDATE_LAST_MODIFIED)
                cursor.close()

            self.logger.info(LogMessages.DB_CONNECTED)
            self.__class__._initialized = True
        except Exception as e:
            self.logger.exception(LogMessages.format_safe(LogMessages.DB_CONNECTION_ERROR, error=str(e)))
            raise

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConfig, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls, echo: bool = False) -> Self:
        if cls._instance is None:
            cls._instance = cls(echo=echo)
        return cls._instance
    
    @property
    def get_engine(self) -> Engine:
        return self.engine