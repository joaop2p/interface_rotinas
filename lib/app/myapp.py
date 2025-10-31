from lib.src.core.page_manager import PageManager
from flet import Page

class MyApp:
    _NAME = "Gerenciador de Rotinas"
    _VERSION = "1.0.0"

    def __init__(self):
        print("Initializing MyApp...")
        self._page_manager = PageManager()

    def run(self, page: Page):
        print('a')
        print(f"Running {self._NAME} version {self._VERSION}")
        self._page_manager.set_page(page)
        page.go('/home')