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
        accounts_payable = self._build_new_accounts_payable(payload, now)
        return self._save(accounts_payable)

    def list(self) -> list[AccountsPayableOut]:
        """Lista todas as contas a pagar cadastradas."""

        return [accounts_payable.model_copy(deep=True) for accounts_payable in self._accounts_payable.values()]

    def get_by_id(self, accounts_payable_id: UUID) -> AccountsPayableOut | None:
        """Busca uma conta a pagar pelo identificador."""

        return self._copy(self._accounts_payable.get(accounts_payable_id))

    def update(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayableUpdate,
    ) -> AccountsPayableOut | None:
        """Atualiza campos permitidos de uma conta a pagar existente."""

        return self._update_stored(
            accounts_payable_id,
            payload.model_dump(exclude_none=True),
        )

    def register_payment(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayablePaymentCreate,
    ) -> AccountsPayableOut | None:
        """Registra o pagamento de uma conta a pagar."""

        return self._update_stored(
            accounts_payable_id,
            {
                "status": AccountsPayableStatus.PAID,
                "data_pagamento": payload.data_pagamento,
                "valor_pago": payload.valor_pago,
                "observacao_pagamento": payload.observacao_pagamento,
            },
        )

    def transition_status(
        self,
        accounts_payable_id: UUID,
        status: AccountsPayableStatus,
    ) -> AccountsPayableOut | None:
        """Atualiza o status de uma conta a pagar."""

        return self._update_stored(accounts_payable_id, {"status": status})

    def _build_new_accounts_payable(
        self,
        payload: AccountsPayableCreate,
        now: datetime,
    ) -> AccountsPayableOut:
        """Monta a entidade persistida para um novo cadastro."""

        return AccountsPayableOut(
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

    def _update_stored(
        self,
        accounts_payable_id: UUID,
        changes: dict[str, object],
    ) -> AccountsPayableOut | None:
        """Aplica mudancas no registro persistido e devolve copia isolada."""

        current = self._accounts_payable.get(accounts_payable_id)
        if current is None:
            return None

        updated_accounts_payable = current.model_copy(
            update={
                **changes,
                "atualizado_em": datetime.now(UTC),
            },
            deep=True,
        )
        return self._save(updated_accounts_payable)

    def _save(self, accounts_payable: AccountsPayableOut) -> AccountsPayableOut:
        """Persiste a entidade em memoria e devolve copia defensiva."""

        self._accounts_payable[accounts_payable.id] = accounts_payable
        return accounts_payable.model_copy(deep=True)

    def _copy(self, accounts_payable: AccountsPayableOut | None) -> AccountsPayableOut | None:
        """Devolve copia defensiva do registro quando existente."""

        if accounts_payable is None:
            return None
        return accounts_payable.model_copy(deep=True)
