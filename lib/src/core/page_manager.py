from typing import Callable, Self
from flet import Page, RouteChangeEvent
from lib.src.core.routes import Routes
from lib.src.models.interfaces.view_template import ViewTemplate
from lib.src.views import HomeView, AddCategoriesView, AddRoutinesView

class PageManager:
    _current_page: ViewTemplate | None
    _page: Page
    _instance = None
    _routes: dict[str, ViewTemplate | Callable[[], ViewTemplate]] = {
        Routes.HOME: HomeView(),
        Routes.CATEGORIES_NEW: AddCategoriesView,
        Routes.ROUTINES_NEW: AddRoutinesView,
    }

    def __init__(self):
        print("Initializing PageManager...")
        self._current_page = HomeView()

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super(PageManager, cls).__new__(cls)
            cls._instance._current_page = None
        return cls._instance

    def _change_page(self, event: RouteChangeEvent) -> None:
        route = getattr(event, 'route', None) or getattr(event, 'data', None)
        if route is None or route not in self._routes:
            route = Routes.HOME
        page_entry = self._routes[route]
        if callable(page_entry):
            new_view = page_entry()
        else:
            new_view = page_entry
        new_view.set_page(self._page)
        self._page.views.clear()
        self._page.views.append(new_view.get_view())
        self._page.update()

    def _view_pop(self, view) -> None:
        self._page.views.pop()
        top_view = self._page.views[-1]
        if top_view.route:
            self._page.go(top_view.route)

    def set_page(self, page: Page):
        self._page = page
        self._page.on_route_change = self._change_page
        self._page.on_view_pop = self._view_pop