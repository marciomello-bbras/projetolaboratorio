from __future__ import annotations

from uuid import UUID

from app.models.accounts_payable import (
    AccountsPayableCreate,
    AccountsPayableOut,
    AccountsPayableStatus,
    AccountsPayableUpdate,
)
from app.repositories.accounts_payable_repository import AccountsPayableRepository
from app.services.priority_advisor import PriorityAdvisor


class AccountsPayableNotFoundError(Exception):
    """Erro para conta a pagar nao encontrada."""


class AccountsPayableService:
    """Servico com regras de negocio de contas a pagar."""

    def __init__(
        self,
        repository: AccountsPayableRepository,
        priority_advisor: PriorityAdvisor,
    ) -> None:
        self._repository = repository
        self._priority_advisor = priority_advisor

    def create(
        self,
        payload: AccountsPayableCreate,
        *,
        suggest_priority: bool = True,
    ) -> AccountsPayableOut:
        """Cria uma conta a pagar aplicando sugestao de prioridade."""

        accounts_payable_payload = payload
        if suggest_priority:
            accounts_payable_payload = payload.model_copy(
                update={
                    "priority": self._priority_advisor.suggest_priority(
                        title=payload.title,
                        description=payload.description,
                        due_date=payload.due_date,
                        status=AccountsPayableStatus.PENDING,
                    )
                }
            )

        return self._repository.create(accounts_payable_payload)

    def list(self) -> list[AccountsPayableOut]:
        """Lista todas as contas a pagar."""

        return self._repository.list()

    def get_by_id(self, accounts_payable_id: UUID) -> AccountsPayableOut:
        """Retorna uma conta a pagar pelo identificador."""

        accounts_payable = self._repository.get_by_id(accounts_payable_id)
        if accounts_payable is None:
            raise AccountsPayableNotFoundError(
                f"conta a pagar '{accounts_payable_id}' nao encontrada"
            )
        return accounts_payable

    def update(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayableUpdate,
        *,
        suggest_priority: bool = False,
    ) -> AccountsPayableOut:
        """Atualiza uma conta a pagar existente."""

        current_accounts_payable = self.get_by_id(accounts_payable_id)
        update_payload = payload

        if suggest_priority and payload.priority is None:
            next_status = payload.status or current_accounts_payable.status
            suggested_priority = self._priority_advisor.suggest_priority(
                title=payload.title or current_accounts_payable.title,
                description=payload.description
                if payload.description is not None
                else current_accounts_payable.description,
                due_date=payload.due_date
                if payload.due_date is not None
                else current_accounts_payable.due_date,
                status=next_status,
            )
            update_payload = payload.model_copy(update={"priority": suggested_priority})

        updated_accounts_payable = self._repository.update(accounts_payable_id, update_payload)
        if updated_accounts_payable is None:
            raise AccountsPayableNotFoundError(
                f"conta a pagar '{accounts_payable_id}' nao encontrada"
            )
        return updated_accounts_payable

    def delete(self, accounts_payable_id: UUID) -> None:
        """Remove uma conta a pagar existente."""

        deleted = self._repository.delete(accounts_payable_id)
        if not deleted:
            raise AccountsPayableNotFoundError(
                f"conta a pagar '{accounts_payable_id}' nao encontrada"
            )
