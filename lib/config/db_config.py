import logging
from os import getenv, makedirs
from sqlalchemy import Engine, create_engine, event
from contextlib import contextmanager
from sqlmodel import SQLModel, Session
from . import CONFIG_CONSTANTS, LOG_CONSTANTS as LOG
from typing import Self, Any
from ..src.models.db.models import *

class DatabaseConfig:
    _instance = None
    _initialized = False

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
        
        if CONFIG_CONSTANTS.DATABASE_PATH is None:
            path = CONFIG_CONSTANTS.ALTERNATIVE_PATH
            makedirs(path, exist_ok=True)
            path = f"{path}/routines.sqlite"
        else:
            path = CONFIG_CONSTANTS.DATABASE_PATH
        url = f"sqlite:///{path}"
        try:
            self.logger.debug(LOG.DB_CONNECTING, {"db_path": url})
            is_sqlite = url.startswith("sqlite:")
            engine_kwargs: dict[str, Any] = {
                "echo": echo or (getenv("DB_ECHO", "false").lower() == "true"),
                "future": True,
                "pool_pre_ping": True,
            }

            if is_sqlite:
                # Para SQLite, evitar parâmetros de QueuePool que causam TypeError
                # e permitir acesso multi-thread quando necessário
                engine_kwargs["connect_args"] = {"check_same_thread": False}
            else:
                # Parâmetros de pool para bancos não-SQLite
                try:
                    pool_size = int(getenv("DB_POOL_SIZE", "5"))
                    max_overflow = int(getenv("DB_MAX_OVERFLOW", "10"))
                    pool_recycle = int(getenv("DB_POOL_RECYCLE", "1800"))
                except ValueError:
                    # Fallback seguro caso variáveis estejam malformadas
                    pool_size, max_overflow, pool_recycle = 5, 10, 1800

                engine_kwargs.update(
                    {
                        "pool_size": pool_size,
                        "max_overflow": max_overflow,
                        "pool_recycle": pool_recycle,
                    }
                )

            self.engine: Engine = create_engine(url, **engine_kwargs)

            # Habilita FK no SQLite
            if is_sqlite:
                @event.listens_for(self.engine, "connect")
                def _set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()

            SQLModel.metadata.create_all(self.engine)
            self.logger.info(LOG.DB_CONNECTED)
            self.__class__._initialized = True
        except Exception as e:
            self.logger.exception(LOG.DB_CONNECTION_ERROR, {"error": str(e)})
            raise

    def __new__(cls, *args, **kwargs) -> Self:
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