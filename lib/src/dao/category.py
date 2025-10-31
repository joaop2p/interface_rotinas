from lib.config.db_config import DatabaseConfig
from sqlmodel import Session, select

from lib.src.models.db.models import Category


class CategoryDAO(DatabaseConfig):
    def __init__(self):
        super().__init__()

    def get_all_categories(self):
        with Session(self.engine) as session:
            categories = session.exec(select(Category)).all()
            return categories