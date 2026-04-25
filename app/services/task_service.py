from __future__ import annotations

from uuid import UUID

from app.models.task import TaskCreate, TaskOut, TaskStatus, TaskUpdate
from app.repositories.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor


class TaskNotFoundError(Exception):
    """Erro para tarefa nao encontrada."""


class TaskService:
    """Servico com regras de negocio de tarefas."""

    def __init__(
        self,
        repository: TaskRepository,
        priority_advisor: PriorityAdvisor,
    ) -> None:
        self._repository = repository
        self._priority_advisor = priority_advisor

    def create(self, payload: TaskCreate, *, suggest_priority: bool = True) -> TaskOut:
        """Cria uma tarefa aplicando regra de prioridade quando necessario."""

        task_payload = payload
        if suggest_priority:
            task_payload = payload.model_copy(
                update={
                    "priority": self._priority_advisor.suggest_priority(
                        title=payload.title,
                        description=payload.description,
                        due_date=payload.due_date,
                        status=TaskStatus.PENDING,
                    )
                }
            )

        return self._repository.create(task_payload)

    def list(self) -> list[TaskOut]:
        """Lista todas as tarefas."""

        return self._repository.list()

    def get_by_id(self, task_id: UUID) -> TaskOut:
        """Retorna uma tarefa pelo identificador."""

        task = self._repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"tarefa '{task_id}' nao encontrada")
        return task

    def update(self, task_id: UUID, payload: TaskUpdate, *, suggest_priority: bool = False) -> TaskOut:
        """Atualiza uma tarefa existente."""

        current_task = self.get_by_id(task_id)
        update_payload = payload

        if suggest_priority and payload.priority is None:
            next_status = payload.status or current_task.status
            suggested_priority = self._priority_advisor.suggest_priority(
                title=payload.title or current_task.title,
                description=payload.description
                if payload.description is not None
                else current_task.description,
                due_date=payload.due_date if payload.due_date is not None else current_task.due_date,
                status=next_status,
            )
            update_payload = payload.model_copy(update={"priority": suggested_priority})

        updated_task = self._repository.update(task_id, update_payload)
        if updated_task is None:
            raise TaskNotFoundError(f"tarefa '{task_id}' nao encontrada")
        return updated_task

    def delete(self, task_id: UUID) -> None:
        """Remove uma tarefa existente."""

        deleted = self._repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"tarefa '{task_id}' nao encontrada")
