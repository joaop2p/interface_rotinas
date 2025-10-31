from dotenv import load_dotenv
from lib.config.constants import ConfigDefaults, LogMessages
from lib.config.settings import Config

load_dotenv()
CONFIG_CONSTANTS = ConfigDefaults()
LOG_CONSTANTS = LogMessages()
Config()