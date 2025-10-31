from typing import Sequence, Any, cast
from lib.config.db_config import DatabaseConfig
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from lib.src.models.db.models import Routine

class RoutinesDAO(DatabaseConfig):
    def __init__(self) -> None:
        super().__init__()
    
    def get_all_routines(self) -> Sequence[Routine]:
        with Session(self.engine) as session:
            # Carrega a categoria junto para permitir acesso a routine.category.icon fora da sessão
            # Cast para Any para satisfazer o type checker (Pylance/SQLAlchemy typings)
            statement = select(Routine).options(joinedload(cast(Any, Routine.category)))
            result = session.exec(statement)
            return result.all()
