from os import getenv, getlogin
from dotenv import load_dotenv

class SQLConstants:
    TRIGGER_UPDATE_LAST_MODIFIED = """
    CREATE TRIGGER IF NOT EXISTS update_last_modified
    AFTER UPDATE ON tb_routines
    BEGIN
        UPDATE tb_routines SET dt_modified = CURRENT_TIMESTAMP WHERE routine_id = NEW.routine_id;
    END;
    """
    ACTIVE_FOREIGN_KEYS = "PRAGMA foreign_keys=ON;"

class AppConstants:
    APP_NAME: str = "Scripts Hub"
    VERSION: str = "1.0.0"
    # Application paths
    USER_DATA_PATH: str = rf'C:\users\{getlogin()}\AppData\Local\{APP_NAME}'
    USER_LOGS_PATH: str = rf'{USER_DATA_PATH}\logs'
    USER_DB_PATH: str = rf'{USER_DATA_PATH}\database'
    DEFAULT_DB_NAME: str = "rotinas.sqlite"
    DEFAULT_LOG_NAME: str = "app.log"
    DEFAULT_DIR: str = rf'C:\users\{getlogin()}\documents'
    # Terminal log settings
    TERMINAL_LIMIT: int = 100
    TERMINAL_UPDATE_INTERVAL: float = 1.0
    # Seletor de arquivos
    PYTHON_EXTENSIONS: list[str] = ["py", "pyc", "pyo", "pyd", "pyw", "pyz"]
    FILE_PICKER_TITLE: str = "Selecione um arquivo Python"
    # Captura de logs
    MAX_LOG_LINES: int = 1000

    @classmethod
    def get_database_path(cls) -> str:
        """Retorna caminho completo do banco SQLite"""
        from os import makedirs
        from os.path import join
        
        makedirs(cls.USER_DB_PATH, exist_ok=True)
        return join(cls.USER_DB_PATH, cls.DEFAULT_DB_NAME)
    
    @classmethod
    def get_log_file_path(cls) -> str:
        """Retorna caminho completo do arquivo de log"""
        from os import makedirs
        from os.path import join
        
        makedirs(cls.USER_LOGS_PATH, exist_ok=True)
        return join(cls.USER_LOGS_PATH, cls.DEFAULT_LOG_NAME)
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Garante que todos os diretórios necessários existam"""
        from os import makedirs
        makedirs(cls.USER_DB_PATH, exist_ok=True)
        makedirs(cls.USER_LOGS_PATH, exist_ok=True)

class LogMessages:
    """Repositório centralizado de mensagens de LOG."""
    
    # === INICIALIZAÇÃO ===
    APP_STARTING = "Inicializando %(app_name)s v%(version)s."
    APP_STARTED = "%(app_name)s inicializado."
    APP_STOPPING = "Finalizando %(app_name)s."
    APP_STOPPED = "%(app_name)s finalizado."
    
    CONFIG_LOADING = "Carregando configurações de %(config_file)s."
    CONFIG_LOADED = "Configurações carregadas."
    CONFIG_ERROR = "Falha ao carregar configurações: %(error)s."
    CONFIG_FILE_NOT_FOUND = "Arquivo de configuração não localizado: %(file_path)s."
    CONFIG_VALIDATION_ERROR = "Configuração inválida: %(detail)s."
    
    # === BANCO DE DADOS ===
    DB_CONNECTING = "Conectando ao banco de dados: %(db_path)s."
    DB_CONNECTED = "Conexão com o banco de dados estabelecida."
    DB_CONNECTION_ERROR = "Falha na conexão com o banco de dados: %(error)s."
    DB_QUERY_EXECUTING = "Executando consulta SQL: %(query)s."
    DB_QUERY_SUCCESS = "Consulta executada com êxito. Registros afetados: %(rows)d."
    DB_QUERY_ERROR = "Erro na execução da consulta: %(error)s."
    DB_BACKUP_CREATING = "Iniciando backup do banco de dados."
    DB_BACKUP_SUCCESS = "Backup concluído em %(backup_path)s."
    DB_BACKUP_ERROR = "Falha ao criar backup: %(error)s."
    
    # === ARQUIVOS ===
    FILE_READING = "Lendo arquivo: %(file_path)s."
    FILE_READ_SUCCESS = "Leitura concluída: %(file_path)s."
    FILE_READ_ERROR = "Falha na leitura do arquivo %(file_path)s: %(error)s."
    FILE_WRITING = "Gravando arquivo: %(file_path)s."
    FILE_WRITE_SUCCESS = "Gravação concluída: %(file_path)s."
    FILE_WRITE_ERROR = "Falha na gravação do arquivo %(file_path)s: %(error)s."
    FILE_NOT_FOUND = "Arquivo não encontrado: %(file_path)s."
    FILE_PERMISSION_ERROR = "Permissão negada ao acessar o arquivo: %(file_path)s."
    FILE_PROCESSING = "Processando arquivo: %(file_path)s."
    FILE_PROCESSED = "Processamento concluído: %(file_path)s."
    
    # === DIRETÓRIOS ===
    DIR_CREATING = "Criando diretório: %(dir_path)s."
    DIR_CREATED = "Diretório criado: %(dir_path)s."
    DIR_EXISTS = "Diretório já existente: %(dir_path)s."
    DIR_ERROR = "Falha ao criar diretório %(dir_path)s: %(error)s."
    
    # === SELENIUM/DRIVER ===
    DRIVER_STARTING = "Inicializando driver do navegador."
    DRIVER_STARTED = "Driver inicializado."
    DRIVER_ERROR = "Falha ao inicializar o driver: %(error)s."
    DRIVER_STOPPING = "Encerrando driver do navegador."
    DRIVER_STOPPED = "Driver encerrado."

    @classmethod
    def format_safe(cls, template: str, **kwargs) -> str:
        """Formata mensagem com tratamento de erro seguro"""
        try:
            return template % kwargs
        except (KeyError, TypeError, ValueError) as e:
            return f"Erro ao formatar log '{template[:50]}...': {e}"
    
    @classmethod
    def get_startup_message(cls) -> str:
        """Retorna mensagem formatada de inicialização"""
        from . import AppConstants
        return cls.format_safe(
            cls.APP_STARTING,
            app_name=AppConstants.APP_NAME,
            version=AppConstants.VERSION
        )