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

        return self._sync_overdue_statuses(self._repository.list())

    def list_overdue(self) -> list[AccountsPayableOut]:
        """Lista contas a pagar vencidas."""

        return [
            accounts_payable
            for accounts_payable in self._sync_overdue_statuses(self._repository.list())
            if accounts_payable.status == AccountsPayableStatus.OVERDUE
        ]

    def get_by_id(self, accounts_payable_id: UUID) -> AccountsPayableOut:
        """Retorna uma conta a pagar pelo identificador."""

        return self._get_by_id_or_raise(accounts_payable_id)

    def update(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayableUpdate,
    ) -> AccountsPayableOut:
        """Atualiza uma conta a pagar existente."""

        current_accounts_payable = self._get_by_id_or_raise(accounts_payable_id)
        self._ensure_updatable(current_accounts_payable)
        self._validate_update_dates(current_accounts_payable, payload)

        updated_accounts_payable = self._repository.update(accounts_payable_id, payload)
        if updated_accounts_payable is None:
            raise self._not_found(accounts_payable_id)
        return self._sync_overdue_status(updated_accounts_payable)

    def delete(self, accounts_payable_id: UUID) -> None:
        """Bloqueia a remocao fisica para preservar rastreabilidade."""

        self._get_by_id_or_raise(accounts_payable_id)
        raise AccountsPayableDeletionBlockedError(
            "remocao fisica nao e permitida; cancele a conta para preserva-la"
        )

    def register_payment(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayablePaymentCreate,
    ) -> AccountsPayableOut:
        """Registra o pagamento de uma conta a pagar."""

        current_accounts_payable = self._get_by_id_or_raise(accounts_payable_id)
        self._ensure_payable(current_accounts_payable, payload)

        paid_accounts_payable = self._repository.register_payment(accounts_payable_id, payload)
        if paid_accounts_payable is None:
            raise self._not_found(accounts_payable_id)
        return paid_accounts_payable

    def transition_status(
        self,
        accounts_payable_id: UUID,
        payload: AccountsPayableStatusUpdate,
    ) -> AccountsPayableOut:
        """Atualiza o status de uma conta a pagar com regras de dominio."""

        current_accounts_payable = self._get_by_id_or_raise(accounts_payable_id)
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
            raise self._not_found(accounts_payable_id)
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

    def _sync_overdue_status(self, accounts_payable: AccountsPayableOut) -> AccountsPayableOut:
        """Mantem o status vencido coerente com a data atual."""

        if accounts_payable.status in {
            AccountsPayableStatus.PAID,
            AccountsPayableStatus.CANCELLED,
        }:
            return accounts_payable

        expected_status = (
            AccountsPayableStatus.OVERDUE
            if self._is_overdue(accounts_payable)
            else AccountsPayableStatus.PENDING
        )
        if accounts_payable.status == expected_status:
            return accounts_payable

        synchronized_accounts_payable = self._repository.transition_status(
            accounts_payable.id,
            expected_status,
        )
        if synchronized_accounts_payable is None:
            raise self._not_found(accounts_payable.id)
        return synchronized_accounts_payable

    def _sync_overdue_statuses(
        self,
        accounts_payable_list: list[AccountsPayableOut],
    ) -> list[AccountsPayableOut]:
        """Sincroniza status vencido para uma lista de contas."""

        return [self._sync_overdue_status(accounts_payable) for accounts_payable in accounts_payable_list]

    def _get_by_id_or_raise(self, accounts_payable_id: UUID) -> AccountsPayableOut:
        """Busca conta pelo id e falha com erro de dominio quando ausente."""

        accounts_payable = self._repository.get_by_id(accounts_payable_id)
        if accounts_payable is None:
            raise self._not_found(accounts_payable_id)
        return self._sync_overdue_status(accounts_payable)

    def _not_found(self, accounts_payable_id: UUID) -> AccountsPayableNotFoundError:
        """Constroi erro padrao de conta inexistente."""

        return AccountsPayableNotFoundError(
            f"conta a pagar '{accounts_payable_id}' nao encontrada"
        )

    def _ensure_updatable(self, accounts_payable: AccountsPayableOut) -> None:
        """Valida se a conta pode receber atualizacao cadastral."""

        if accounts_payable.status == AccountsPayableStatus.CANCELLED:
            raise AccountsPayableInvalidStateError(
                "conta a pagar cancelada nao pode ser atualizada"
            )
        if accounts_payable.status == AccountsPayableStatus.PAID:
            raise AccountsPayableInvalidStateError(
                "conta a pagar paga nao pode ser atualizada"
            )

    def _validate_update_dates(
        self,
        current_accounts_payable: AccountsPayableOut,
        payload: AccountsPayableUpdate,
    ) -> None:
        """Valida coerencia das datas apos aplicar os campos do update."""

        data_emissao = payload.data_emissao or current_accounts_payable.data_emissao
        data_vencimento = payload.data_vencimento or current_accounts_payable.data_vencimento
        if data_emissao is not None and data_emissao > data_vencimento:
            raise AccountsPayableInvalidStateError(
                "data_emissao nao pode ser posterior a data_vencimento"
            )

    def _ensure_payable(
        self,
        current_accounts_payable: AccountsPayableOut,
        payload: AccountsPayablePaymentCreate,
    ) -> None:
        """Valida se a conta pode ser liquidada com os dados informados."""

        if current_accounts_payable.status == AccountsPayableStatus.CANCELLED:
            raise AccountsPayableInvalidStateError(
                "conta a pagar cancelada nao pode ser marcada como paga"
            )
        if current_accounts_payable.status == AccountsPayableStatus.PAID:
            raise AccountsPayableInvalidStateError(
                "conta a pagar ja foi marcada como paga"
            )
        if payload.valor_pago != current_accounts_payable.valor_previsto:
            raise AccountsPayableInvalidStateError(
                "valor_pago deve ser igual ao valor_previsto para liquidar a conta"
            )
        if (
            current_accounts_payable.data_emissao is not None
            and payload.data_pagamento < current_accounts_payable.data_emissao
        ):
            raise AccountsPayableInvalidStateError(
                "data_pagamento nao pode ser anterior a data_emissao"
            )
