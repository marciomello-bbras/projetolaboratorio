from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskStatus(StrEnum):
    """Status suportados para a tarefa."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    """Prioridades suportadas para a tarefa."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskBase(BaseModel):
    """Campos compartilhados da tarefa."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    title: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Titulo curto da tarefa.",
        examples=["Validar pagamento do fornecedor XPTO"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detalhes opcionais da tarefa.",
    )
    due_date: date | None = Field(
        default=None,
        description="Data prevista para conclusao.",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Nivel de prioridade da tarefa.",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Rejeita titulos em branco."""

        if not value.strip():
            raise ValueError("o titulo nao pode estar em branco")
        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        """Normaliza a descricao opcional."""

        if value is None:
            return None

        value = value.strip()
        return value or None


class TaskCreate(TaskBase):
    """Payload de criacao da tarefa."""


class TaskUpdate(BaseModel):
    """Payload de atualizacao da tarefa."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=120,
        description="Titulo curto da tarefa.",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detalhes opcionais da tarefa.",
    )
    due_date: date | None = Field(
        default=None,
        description="Data prevista para conclusao.",
    )
    priority: TaskPriority | None = Field(
        default=None,
        description="Nivel de prioridade da tarefa.",
    )
    status: TaskStatus | None = Field(
        default=None,
        description="Status do ciclo de vida da tarefa.",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        """Rejeita titulos em branco quando informados."""

        if value is None:
            return None
        if not value.strip():
            raise ValueError("o titulo nao pode estar em branco")
        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        """Normaliza a descricao opcional."""

        if value is None:
            return None

        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_has_updates(self) -> "TaskUpdate":
        """Exige ao menos um campo para atualizacao."""

        if self.model_dump(exclude_none=True) == {}:
            raise ValueError("informe ao menos um campo para atualizacao")
        return self


class TaskOut(TaskBase):
    """Schema de resposta da tarefa."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Identificador unico da tarefa.")
    status: TaskStatus = Field(..., description="Status do ciclo de vida da tarefa.")
    created_at: datetime = Field(..., description="Data e hora de criacao.")
    updated_at: datetime = Field(..., description="Data e hora da ultima atualizacao.")
