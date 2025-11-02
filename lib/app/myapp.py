from lib.src.core.page_manager import PageManager
from flet import Page
import logging

class MyApp:
    _NAME = "Gerenciador de Rotinas"
    _VERSION = "1.0.0"

    def __init__(self):
        self.logger = logging.getLogger('AppRoot')
        self._page_manager = PageManager()

    def run(self, page: Page):
        self.logger.info(f"Running {self._NAME} version {self._VERSION}")
        self._page_manager.set_page(page)
        page.go('/home')