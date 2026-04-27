from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.models.accounts_payable import (
    AccountsPayableCreate,
    AccountsPayableOut,
    AccountsPayablePaymentCreate,
    AccountsPayableStatus,
    AccountsPayableUpdate,
)


class AccountsPayableRepository:
    """Repositorio em memoria para contas a pagar."""

    def __init__(self) -> None:
        self._accounts_payable: dict[UUID, AccountsPayableOut] = {}

    def create(self, payload: AccountsPayableCreate) -> AccountsPayableOut:
        """Cria uma conta a pagar e armazena em memoria."""

        now = datetime.now(UTC)
        accounts_payable = AccountsPayableOut(
            id=uuid4(),
            descricao=payload.descricao,
            fornecedor_ou_favorecido=payload.fornecedor_ou_favorecido,
            categoria=payload.categoria,
            valor_previsto=payload.valor_previsto,
            data_vencimento=payload.data_vencimento,
            centro_de_custo=payload.centro_de_custo,
            data_emissao=payload.data_emissao,
            observacoes=payload.observacoes,
            status=AccountsPayableStatus.PENDING,
            data_pagamento=None,
            valor_pago=None,
            observacao_pagamento=None,
            criado_em=now,
            atualizado_em=now,
        )
        self._accounts_payable[accounts_payable.id] = accounts_payable
        return accounts_payable.model_copy(deep=True)

    def list(self) -> list[AccountsPayableOut]:
        """Lista todas as contas a pagar cadastradas."""

        return [accounts_payable.model_copy(deep=True) for accounts_payable in self._accounts_payable.values()]

    def get_by_id(self, accounts_payable_id: UUID) -> AccountsPayableOut | None:
        """Busca uma conta a pagar pelo identificador."""

        accounts_payable = self._accounts_payable.get(accounts_payable_id)
        if accounts_payable is None:
            return None
        return accounts_payable.model_copy(deep=True)

    def update(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayableUpdate,
    ) -> AccountsPayableOut | None:
        """Atualiza campos permitidos de uma conta a pagar existente."""

        current = self._accounts_payable.get(accounts_payable_id)
        if current is None:
            return None

        changes = payload.model_dump(exclude_none=True)
        updated_accounts_payable = current.model_copy(
            update={
                **changes,
                "atualizado_em": datetime.now(UTC),
            },
            deep=True,
        )
        self._accounts_payable[accounts_payable_id] = updated_accounts_payable
        return updated_accounts_payable.model_copy(deep=True)

    def register_payment(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayablePaymentCreate,
    ) -> AccountsPayableOut | None:
        """Registra o pagamento de uma conta a pagar."""

        current = self._accounts_payable.get(accounts_payable_id)
        if current is None:
            return None

        paid_accounts_payable = current.model_copy(
            update={
                "status": AccountsPayableStatus.PAID,
                "data_pagamento": payload.data_pagamento,
                "valor_pago": payload.valor_pago,
                "observacao_pagamento": payload.observacao_pagamento,
                "atualizado_em": datetime.now(UTC),
            },
            deep=True,
        )
        self._accounts_payable[accounts_payable_id] = paid_accounts_payable
        return paid_accounts_payable.model_copy(deep=True)

    def transition_status(
        self,
        accounts_payable_id: UUID,
        status: AccountsPayableStatus,
    ) -> AccountsPayableOut | None:
        """Atualiza o status de uma conta a pagar."""

        current = self._accounts_payable.get(accounts_payable_id)
        if current is None:
            return None

        transitioned_accounts_payable = current.model_copy(
            update={
                "status": status,
                "atualizado_em": datetime.now(UTC),
            },
            deep=True,
        )
        self._accounts_payable[accounts_payable_id] = transitioned_accounts_payable
        return transitioned_accounts_payable.model_copy(deep=True)
