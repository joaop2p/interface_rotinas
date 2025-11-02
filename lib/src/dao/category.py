from lib.config.db_config import DatabaseConfig
from sqlmodel import Session, select

from lib.src.models.db.models import Category


class CategoryDAO:
    def __init__(self):
        self._db_config = DatabaseConfig.get_instance()

    def get_all_categories(self):
        with Session(self._db_config.get_engine) as session:
            categories = session.exec(select(Category)).all()
            return categories
        
    def insert_category(self, category: Category) -> Category:
        with Session(self._db_config.get_engine) as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        
    def delete_category(self, category: Category) -> None:
        with Session(self._db_config.get_engine) as session:
            session.delete(category)
            session.commit()