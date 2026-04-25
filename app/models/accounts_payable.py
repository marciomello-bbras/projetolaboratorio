from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AccountsPayableStatus(StrEnum):
    """Status suportados para a conta a pagar."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AccountsPayablePriority(StrEnum):
    """Prioridades suportadas para a conta a pagar."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccountsPayableBase(BaseModel):
    """Campos compartilhados da conta a pagar."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    title: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Titulo curto da conta a pagar.",
        examples=["Validar pagamento do fornecedor XPTO"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detalhes opcionais da conta a pagar.",
    )
    due_date: date | None = Field(
        default=None,
        description="Data prevista para conclusao.",
    )
    priority: AccountsPayablePriority = Field(
        default=AccountsPayablePriority.MEDIUM,
        description="Nivel de prioridade da conta a pagar.",
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


class AccountsPayableCreate(AccountsPayableBase):
    """Payload de criacao da conta a pagar."""


class AccountsPayableUpdate(BaseModel):
    """Payload de atualizacao da conta a pagar."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=120,
        description="Titulo curto da conta a pagar.",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detalhes opcionais da conta a pagar.",
    )
    due_date: date | None = Field(
        default=None,
        description="Data prevista para conclusao.",
    )
    priority: AccountsPayablePriority | None = Field(
        default=None,
        description="Nivel de prioridade da conta a pagar.",
    )
    status: AccountsPayableStatus | None = Field(
        default=None,
        description="Status do ciclo de vida da conta a pagar.",
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
    def validate_has_updates(self) -> "AccountsPayableUpdate":
        """Exige ao menos um campo para atualizacao."""

        if self.model_dump(exclude_none=True) == {}:
            raise ValueError("informe ao menos um campo para atualizacao")
        return self


class AccountsPayableOut(AccountsPayableBase):
    """Schema de resposta da conta a pagar."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Identificador unico da conta a pagar.")
    status: AccountsPayableStatus = Field(..., description="Status do ciclo de vida da conta a pagar.")
    created_at: datetime = Field(..., description="Data e hora de criacao.")
    updated_at: datetime = Field(..., description="Data e hora da ultima atualizacao.")
