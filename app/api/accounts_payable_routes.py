from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.models.accounts_payable import (
    AccountsPayableCreate,
    AccountsPayableOut,
    AccountsPayablePaymentCreate,
    AccountsPayableStatusUpdate,
    AccountsPayableUpdate,
)
from app.repositories.accounts_payable_repository import AccountsPayableRepository
from app.services.accounts_payable_service import (
    AccountsPayableInvalidStateError,
    AccountsPayableNotFoundError,
    AccountsPayableService,
)
from app.services.priority_advisor import PriorityAdvisor

router = APIRouter(prefix="/accounts-payable", tags=["accounts-payable"])

_repository = AccountsPayableRepository()
_priority_advisor = PriorityAdvisor()
_service = AccountsPayableService(
    repository=_repository,
    priority_advisor=_priority_advisor,
)


def get_accounts_payable_service() -> AccountsPayableService:
    """Retorna a instancia padrao do servico."""

    return _service


ServiceDep = Annotated[AccountsPayableService, Depends(get_accounts_payable_service)]


@router.post(
    "",
    response_model=AccountsPayableOut,
    status_code=status.HTTP_201_CREATED,
)
def create_accounts_payable(
    payload: AccountsPayableCreate,
    service: ServiceDep,
) -> AccountsPayableOut:
    """Cria uma nova conta a pagar."""

    return service.create(payload)


@router.get(
    "",
    response_model=list[AccountsPayableOut],
    status_code=status.HTTP_200_OK,
)
def list_accounts_payable(service: ServiceDep) -> list[AccountsPayableOut]:
    """Lista as contas a pagar cadastradas."""

    return service.list()


@router.get(
    "/overdue",
    response_model=list[AccountsPayableOut],
    status_code=status.HTTP_200_OK,
)
def list_overdue_accounts_payable(service: ServiceDep) -> list[AccountsPayableOut]:
    """Lista as contas a pagar vencidas."""

    return service.list_overdue()


@router.get(
    "/{accounts_payable_id}",
    response_model=AccountsPayableOut,
    status_code=status.HTTP_200_OK,
)
def get_accounts_payable(
    accounts_payable_id: UUID,
    service: ServiceDep,
) -> AccountsPayableOut:
    """Busca uma conta a pagar pelo identificador."""

    try:
        return service.get_by_id(accounts_payable_id)
    except AccountsPayableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put(
    "/{accounts_payable_id}",
    response_model=AccountsPayableOut,
    status_code=status.HTTP_200_OK,
)
def update_accounts_payable(
    accounts_payable_id: UUID,
    payload: AccountsPayableUpdate,
    service: ServiceDep,
) -> AccountsPayableOut:
    """Atualiza uma conta a pagar existente."""

    try:
        return service.update(accounts_payable_id, payload)
    except AccountsPayableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/{accounts_payable_id}/payment",
    response_model=AccountsPayableOut,
    status_code=status.HTTP_200_OK,
)
def register_accounts_payable_payment(
    accounts_payable_id: UUID,
    payload: AccountsPayablePaymentCreate,
    service: ServiceDep,
) -> AccountsPayableOut:
    """Registra o pagamento de uma conta a pagar."""

    try:
        return service.register_payment(accounts_payable_id, payload)
    except AccountsPayableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AccountsPayableInvalidStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch(
    "/{accounts_payable_id}/status",
    response_model=AccountsPayableOut,
    status_code=status.HTTP_200_OK,
)
def transition_accounts_payable_status(
    accounts_payable_id: UUID,
    payload: AccountsPayableStatusUpdate,
    service: ServiceDep,
) -> AccountsPayableOut:
    """Atualiza o status de uma conta a pagar."""

    try:
        return service.transition_status(accounts_payable_id, payload)
    except AccountsPayableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AccountsPayableInvalidStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/{accounts_payable_id}/cancel",
    response_model=AccountsPayableOut,
    status_code=status.HTTP_200_OK,
)
def cancel_accounts_payable(
    accounts_payable_id: UUID,
    service: ServiceDep,
) -> AccountsPayableOut:
    """Cancela uma conta a pagar."""

    try:
        return service.cancel(accounts_payable_id)
    except AccountsPayableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AccountsPayableInvalidStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/{accounts_payable_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_accounts_payable(
    accounts_payable_id: UUID,
    service: ServiceDep,
) -> Response:
    """Remove uma conta a pagar existente."""

    try:
        service.delete(accounts_payable_id)
    except AccountsPayableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
