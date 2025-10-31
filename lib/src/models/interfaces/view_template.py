from abc import ABC, abstractmethod
from flet import Page, View

class ViewTemplate(ABC):
    _page: Page | None
    _title: str
    _route: str

    @abstractmethod
    def get_view(self) -> View:
        pass
    @abstractmethod
    def set_page(self, page: Page) -> None:
        pass