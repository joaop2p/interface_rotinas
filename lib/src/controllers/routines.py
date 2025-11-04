from typing import Sequence
from lib.src.models.db.models import Routine
from lib.src.services.routines import RoutinesService


class RoutinesController:
    def __init__(self):
        self.service = RoutinesService()

    def get_all_routines(self) -> Sequence[Routine]:
        return self.service.get_all_routines()

    def get_by_id(self, routine_id: int) -> Routine | None:
        return self.service.get_by_id(routine_id)

    def insert_routine(self, name: str, path: str, desc: str, category_id: int) -> Routine:
        routine = Routine(
            routine_name=name,
            directory_path=path,
            description=desc,
            category_id=category_id
        )
        return self.service.insert_routine(routine)
    
    def delete_routine(self, routine: Routine) -> None:
        pass

    def update_routine(self, routine_id: int | None, name: str, description: str, directory_path: str, category_id: int) -> Routine:
        """Atualiza uma rotina existente com validações"""
        if routine_id is None:
            raise ValueError("ID da rotina é obrigatório para atualização")

        import os
        from lib.config import AppConstants
        
        # Validação de campos obrigatórios
        if not name or not name.strip():
            raise ValueError("Nome da rotina é obrigatório")
        
        if not description or not description.strip():
            raise ValueError("Descrição da rotina é obrigatória")
        
        if not directory_path or not directory_path.strip():
            raise ValueError("Caminho do arquivo é obrigatório")
        
        # Validação do arquivo
        if not os.path.exists(directory_path):
            raise ValueError(f"Arquivo não encontrado: {directory_path}")
        
        if not directory_path.endswith(tuple(AppConstants.PYTHON_EXTENSIONS)):
            raise ValueError("Arquivo deve ser um script Python válido")
        
        # Busca a rotina existente
        existing_routine = self.service.get_by_id(routine_id)
        if not existing_routine:
            raise ValueError(f"Rotina com ID {routine_id} não encontrada")
        
        # Atualiza os campos
        existing_routine.routine_name = name.strip()
        existing_routine.description = description.strip()
        existing_routine.directory_path = directory_path.strip()
        existing_routine.category_id = category_id
        
        return self.service.update_routine(existing_routine)