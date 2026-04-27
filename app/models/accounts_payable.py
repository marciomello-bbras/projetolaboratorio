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

    descricao: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Descricao da conta a pagar.",
        examples=["Pagamento de servicos contabeis de abril"],
    )
    fornecedor_ou_favorecido: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Nome do fornecedor ou favorecido.",
    )
    categoria: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Categoria da conta a pagar.",
    )
    valor_previsto: float = Field(
        ...,
        gt=0,
        description="Valor previsto da conta a pagar.",
    )
    data_vencimento: date = Field(
        ...,
        description="Data de vencimento da conta a pagar.",
    )
    centro_de_custo: str | None = Field(
        default=None,
        max_length=100,
        description="Centro de custo associado, quando informado.",
    )
    data_emissao: date | None = Field(
        default=None,
        description="Data de emissao da conta, quando informada.",
    )
    observacoes: str | None = Field(
        default=None,
        max_length=1000,
        description="Observacoes adicionais da conta a pagar.",
    )

    @field_validator("descricao", "fornecedor_ou_favorecido", "categoria")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """Rejeita textos obrigatorios em branco."""

        if not value.strip():
            raise ValueError("o campo nao pode estar em branco")
        return value

    @field_validator("centro_de_custo", "observacoes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        """Normaliza textos opcionais."""

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

    descricao: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
        description="Descricao da conta a pagar.",
    )
    fornecedor_ou_favorecido: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Nome do fornecedor ou favorecido.",
    )
    categoria: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Categoria da conta a pagar.",
    )
    valor_previsto: float | None = Field(
        default=None,
        gt=0,
        description="Valor previsto da conta a pagar.",
    )
    data_vencimento: date | None = Field(
        default=None,
        description="Data de vencimento da conta a pagar.",
    )
    centro_de_custo: str | None = Field(
        default=None,
        max_length=100,
        description="Centro de custo associado, quando informado.",
    )
    data_emissao: date | None = Field(
        default=None,
        description="Data de emissao da conta, quando informada.",
    )
    observacoes: str | None = Field(
        default=None,
        max_length=1000,
        description="Observacoes adicionais da conta a pagar.",
    )

    @field_validator("descricao", "fornecedor_ou_favorecido", "categoria")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        """Rejeita textos obrigatorios em branco quando informados."""

        if value is None:
            return None
        if not value.strip():
            raise ValueError("o campo nao pode estar em branco")
        return value

    @field_validator("centro_de_custo", "observacoes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        """Normaliza textos opcionais."""

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

    data_pagamento: date = Field(
        ...,
        description="Data em que o pagamento foi realizado.",
    )
    valor_pago: float = Field(
        ...,
        gt=0,
        description="Valor efetivamente pago.",
    )
    observacao_pagamento: str | None = Field(
        default=None,
        max_length=500,
        description="Observacao opcional do pagamento.",
    )

    @field_validator("observacao_pagamento")
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
    data_pagamento: date | None = Field(None, description="Data em que o pagamento foi realizado.")
    valor_pago: float | None = Field(None, description="Valor efetivamente pago.")
    observacao_pagamento: str | None = Field(None, description="Observacao opcional do pagamento.")
    criado_em: datetime = Field(..., description="Data e hora de criacao.")
    atualizado_em: datetime = Field(..., description="Data e hora da ultima atualizacao.")
