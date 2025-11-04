from typing import Sequence, Any, cast
from lib.config.db_config import DatabaseConfig
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from lib.src.models.db.models import Routine

class RoutinesDAO:
    def __init__(self) -> None:
        self._db_config = DatabaseConfig.get_instance()
    
    def get_all_routines(self) -> Sequence[Routine]:
        with Session(self._db_config.get_engine) as session:
            statement = select(Routine).options(joinedload(cast(Any, Routine.category)))
            result = session.exec(statement)
            routines = result.unique().all()
            return routines

    def get_by_id(self, category_id: int) -> Routine | None:
        with Session(self._db_config.get_engine) as session:
            statement = select(Routine).where(Routine.category_id == category_id).options(joinedload(cast(Any, Routine.category)))
            result = session.exec(statement)
            routine = result.first()
            return routine

    def insert_routine(self, routine: Routine) -> Routine:
        with Session(self._db_config.get_engine) as session:
            session.add(routine)
            session.commit()
            session.refresh(routine)
            return routine

    def update_routine(self, routine: Routine) -> Routine:
        with Session(self._db_config.get_engine) as session:
            merged_routine = session.merge(routine)
            session.commit()
            session.refresh(merged_routine)
            return merged_routine

    def delete_routine(self, routine: Routine) -> None:
        with Session(self._db_config.get_engine) as session:
            session.delete(routine)
            session.commit()