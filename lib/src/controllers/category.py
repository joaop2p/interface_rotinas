from typing import Sequence
from lib.src.models.db.models import Category
from lib.src.services.category import CategoryService


class CategoryController:
    def __init__(self) -> None:
        self.category_service = CategoryService()

    def get_all_categories(self) -> Sequence[Category]:
        return self.category_service.get_all_categories()
    
    def insert_category(self, name: str, icon: str) -> Category:
        new_category = Category(category_name=name, icon=icon)
        return self.category_service.insert_category(new_category)
    
    def delete_category(self, category: Category) -> None:
        self.category_service.delete_category(category)