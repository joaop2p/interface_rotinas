from dotenv import load_dotenv
from .constants import AppConstants, LogMessages, SQLConstants
from .logger import LoggerConfig

def get_config():
    """Retorna a instância do Config apenas quando necessário"""
    return LoggerConfig.get_instance()

def get_logger(name: str):
    """Cria logger apenas quando necessário"""
    return get_config().get_child_logger(name)

__all__ = [
    'AppConstants',
    'LogMessages', 
    'SQLConstants',
    'get_config',  
    'get_logger'   
]