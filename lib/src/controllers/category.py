from typing import Sequence
from lib.src.models.db.models import Category
from lib.src.services.category import CategoryService

class CategoryInUseError(RuntimeError):
    """Categoria possui rotinas associadas."""
    pass

class CategoryController:
    def __init__(self) -> None:
        self.category_service = CategoryService()

    def get_all_categories(self) -> Sequence[Category]:
        return self.category_service.get_all_categories()
    
    def insert_category(self, name: str, icon: str) -> Category:
        new_category = Category(category_name=name, icon=icon)
        return self.category_service.insert_category(new_category)
    
    def delete_category(self, category: Category) -> None:
        from .routines import RoutinesController
        temp_routines_controller = RoutinesController()
        if temp_routines_controller.get_by_category_id(category.category_id):
            raise CategoryInUseError("Não é possível deletar uma categoria que possui rotinas associadas.")
        self.category_service.delete_category(category)