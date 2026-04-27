from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.accounts_payable import (
    AccountsPayableCreate,
    AccountsPayableOut,
    AccountsPayablePaymentCreate,
    AccountsPayableStatus,
    AccountsPayableStatusUpdate,
    AccountsPayableUpdate,
)
from app.repositories.accounts_payable_repository import AccountsPayableRepository


class AccountsPayableNotFoundError(Exception):
    """Erro para conta a pagar nao encontrada."""


class AccountsPayableInvalidStateError(Exception):
    """Erro para transicao invalida de estado."""


class AccountsPayableDeletionBlockedError(Exception):
    """Erro para remocao fisica bloqueada."""


class AccountsPayableService:
    """Servico com regras de negocio de contas a pagar."""

    def __init__(
        self,
        repository: AccountsPayableRepository,
    ) -> None:
        self._repository = repository

    def create(self, payload: AccountsPayableCreate) -> AccountsPayableOut:
        """Cria uma conta a pagar."""

        return self._repository.create(payload)

    def list(self) -> list[AccountsPayableOut]:
        """Lista todas as contas a pagar."""

        return self._repository.list()

    def list_overdue(self) -> list[AccountsPayableOut]:
        """Lista contas a pagar vencidas."""

        overdue_accounts_payable: list[AccountsPayableOut] = []
        for accounts_payable in self._repository.list():
            if self._is_overdue(accounts_payable):
                overdue_accounts_payable.append(
                    accounts_payable.model_copy(update={"status": AccountsPayableStatus.OVERDUE}, deep=True)
                )
        return overdue_accounts_payable

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
    ) -> AccountsPayableOut:
        """Atualiza uma conta a pagar existente."""

        current_accounts_payable = self.get_by_id(accounts_payable_id)
        if current_accounts_payable.status == AccountsPayableStatus.CANCELLED:
            raise AccountsPayableInvalidStateError(
                "conta a pagar cancelada nao pode ser atualizada"
            )

        updated_accounts_payable = self._repository.update(accounts_payable_id, payload)
        if updated_accounts_payable is None:
            raise AccountsPayableNotFoundError(
                f"conta a pagar '{accounts_payable_id}' nao encontrada"
            )
        return updated_accounts_payable

    def delete(self, accounts_payable_id: UUID) -> None:
        """Bloqueia a remocao fisica para preservar rastreabilidade."""

        self.get_by_id(accounts_payable_id)
        raise AccountsPayableDeletionBlockedError(
            "remocao fisica nao e permitida; cancele a conta para preserva-la"
        )

    def register_payment(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayablePaymentCreate,
    ) -> AccountsPayableOut:
        """Registra o pagamento de uma conta a pagar."""

        current_accounts_payable = self.get_by_id(accounts_payable_id)

        if current_accounts_payable.status == AccountsPayableStatus.CANCELLED:
            raise AccountsPayableInvalidStateError(
                "conta a pagar cancelada nao pode ser marcada como paga"
            )

        if current_accounts_payable.status == AccountsPayableStatus.PAID:
            raise AccountsPayableInvalidStateError(
                "conta a pagar ja foi marcada como paga"
            )

        paid_accounts_payable = self._repository.register_payment(accounts_payable_id, payload)
        if paid_accounts_payable is None:
            raise AccountsPayableNotFoundError(
                f"conta a pagar '{accounts_payable_id}' nao encontrada"
            )
        return paid_accounts_payable

    def transition_status(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayableStatusUpdate,
    ) -> AccountsPayableOut:
        """Atualiza o status de uma conta a pagar com regras de dominio."""

        current_accounts_payable = self.get_by_id(accounts_payable_id)
        target_status = payload.status

        if current_accounts_payable.status == target_status:
            return current_accounts_payable

        if current_accounts_payable.status == AccountsPayableStatus.CANCELLED:
            raise AccountsPayableInvalidStateError(
                "conta a pagar cancelada nao pode mudar de status"
            )

        if current_accounts_payable.status == AccountsPayableStatus.PAID:
            raise AccountsPayableInvalidStateError(
                "conta a pagar paga nao pode mudar de status"
            )

        if target_status == AccountsPayableStatus.PENDING:
            raise AccountsPayableInvalidStateError(
                "conta a pagar nao pode retornar para pendente por esta rota"
            )

        if target_status not in {
            AccountsPayableStatus.OVERDUE,
            AccountsPayableStatus.CANCELLED,
        }:
            raise AccountsPayableInvalidStateError(
                "status informado nao e permitido por esta rota"
            )

        transitioned_accounts_payable = self._repository.transition_status(
            accounts_payable_id,
            target_status,
        )
        if transitioned_accounts_payable is None:
            raise AccountsPayableNotFoundError(
                f"conta a pagar '{accounts_payable_id}' nao encontrada"
            )
        return transitioned_accounts_payable

    def cancel(self, accounts_payable_id: UUID) -> AccountsPayableOut:
        """Cancela uma conta a pagar."""

        return self.transition_status(
            accounts_payable_id,
            AccountsPayableStatusUpdate(status=AccountsPayableStatus.CANCELLED),
        )

    def _is_overdue(self, accounts_payable: AccountsPayableOut) -> bool:
        """Indica se a conta a pagar esta vencida na data atual."""

        if accounts_payable.status in {
            AccountsPayableStatus.PAID,
            AccountsPayableStatus.CANCELLED,
        }:
            return False

        today = datetime.now(UTC).date()
        return accounts_payable.data_vencimento < today
