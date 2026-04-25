from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.models.accounts_payable import (
    AccountsPayableCreate,
    AccountsPayableOut,
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
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
            priority=payload.priority,
            status=AccountsPayableStatus.PENDING,
            created_at=now,
            updated_at=now,
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
                "updated_at": datetime.now(UTC),
            },
            deep=True,
        )
        self._accounts_payable[accounts_payable_id] = updated_accounts_payable
        return updated_accounts_payable.model_copy(deep=True)

    def delete(self, accounts_payable_id: UUID) -> bool:
        """Remove uma conta a pagar pelo identificador."""

        return self._accounts_payable.pop(accounts_payable_id, None) is not None
