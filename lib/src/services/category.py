from typing import Sequence
from lib.src.dao.category import CategoryDAO
from lib.src.models.db.models import Category


class CategoryService:
    def __init__(self):
        self.category_dao = CategoryDAO()

    def get_all_categories(self) -> Sequence[Category]:
        return self.category_dao.get_all_categories()
    
    def insert_category(self, category: Category) -> Category:
        return self.category_dao.insert_category(category)
    
    def delete_category(self, category: Category) -> None:
        self.category_dao.delete_category(category)