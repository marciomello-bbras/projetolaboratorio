from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.models.task import TaskCreate, TaskOut, TaskStatus, TaskUpdate


class TaskRepository:
    """Repositorio em memoria para tarefas."""

    def __init__(self) -> None:
        self._tasks: dict[UUID, TaskOut] = {}

    def create(self, payload: TaskCreate) -> TaskOut:
        """Cria uma tarefa e armazena em memoria."""

        now = datetime.now(UTC)
        task = TaskOut(
            id=uuid4(),
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
            priority=payload.priority,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task.id] = task
        return task.model_copy(deep=True)

    def list(self) -> list[TaskOut]:
        """Lista todas as tarefas cadastradas."""

        return [task.model_copy(deep=True) for task in self._tasks.values()]

    def get_by_id(self, task_id: UUID) -> TaskOut | None:
        """Busca uma tarefa pelo identificador."""

        task = self._tasks.get(task_id)
        if task is None:
            return None
        return task.model_copy(deep=True)

    def update(self, task_id: UUID, payload: TaskUpdate) -> TaskOut | None:
        """Atualiza campos permitidos de uma tarefa existente."""

        current = self._tasks.get(task_id)
        if current is None:
            return None

        changes = payload.model_dump(exclude_none=True)
        updated_task = current.model_copy(
            update={
                **changes,
                "updated_at": datetime.now(UTC),
            },
            deep=True,
        )
        self._tasks[task_id] = updated_task
        return updated_task.model_copy(deep=True)

    def delete(self, task_id: UUID) -> bool:
        """Remove uma tarefa pelo identificador."""

        return self._tasks.pop(task_id, None) is not None
