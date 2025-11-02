from typing import Sequence
from sqlalchemy.exc import IntegrityError
from lib.src.dao.category import CategoryDAO
from lib.src.models.db.models import Category


class CategoryInUseError(RuntimeError):
    """Categoria possui rotinas associadas."""
    pass


class CategoryService:
    def __init__(self):
        self.category_dao = CategoryDAO()

    def get_all_categories(self) -> Sequence[Category]:
        return self.category_dao.get_all_categories()
    
    def insert_category(self, category: Category) -> Category:
        return self.category_dao.insert_category(category)
    
    def delete_category(self, category: Category) -> None:
        try:
            self.category_dao.delete_category(category)
        except IntegrityError as e:
            # Requer FK com ON DELETE RESTRICT/NO ACTION habilitado (PRAGMA foreign_keys=ON)
            raise CategoryInUseError("Não é possível deletar uma categoria que possui rotinas associadas.") from e