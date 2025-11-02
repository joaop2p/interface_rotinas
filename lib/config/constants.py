from os import getenv, getlogin
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

class ConfigDefaults:
    APP_NAME: str = "Interface Rotinas"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_PATH: str = getenv("DATABASE_URL")
    ALTERNATIVE_PATH: str = rf'C:\users\{getlogin()}\{APP_NAME}'
    TERMINAL_LIMIT = 100
    TERMINAL_UPDATE_INTERVAL = 0.1

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