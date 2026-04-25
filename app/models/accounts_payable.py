from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AccountsPayableStatus(StrEnum):
    """Status suportados para a conta a pagar."""

    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
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


class AccountsPayableStatusUpdate(BaseModel):
    """Payload de transicao de status da conta a pagar."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    status: AccountsPayableStatus = Field(
        ...,
        description="Novo status da conta a pagar.",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: AccountsPayableStatus) -> AccountsPayableStatus:
        """Restringe status que exigem fluxo dedicado."""

        if value == AccountsPayableStatus.PAID:
            raise ValueError("use a rota de pagamento para marcar a conta como paga")
        return value


class AccountsPayablePaymentCreate(BaseModel):
    """Payload de registro de pagamento."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    payment_date: date = Field(
        ...,
        description="Data em que o pagamento foi realizado.",
    )
    paid_amount: float = Field(
        ...,
        gt=0,
        description="Valor efetivamente pago.",
    )
    payment_note: str | None = Field(
        default=None,
        max_length=500,
        description="Observacao opcional do pagamento.",
    )

    @field_validator("payment_note")
    @classmethod
    def normalize_payment_note(cls, value: str | None) -> str | None:
        """Normaliza a observacao opcional do pagamento."""

        if value is None:
            return None

        value = value.strip()
        return value or None


class AccountsPayableOut(AccountsPayableBase):
    """Schema de resposta da conta a pagar."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Identificador unico da conta a pagar.")
    status: AccountsPayableStatus = Field(..., description="Status do ciclo de vida da conta a pagar.")
    payment_date: date | None = Field(None, description="Data em que o pagamento foi realizado.")
    paid_amount: float | None = Field(None, description="Valor efetivamente pago.")
    payment_note: str | None = Field(None, description="Observacao opcional do pagamento.")
    created_at: datetime = Field(..., description="Data e hora de criacao.")
    updated_at: datetime = Field(..., description="Data e hora da ultima atualizacao.")
