from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.models.accounts_payable import (
    AccountsPayableCreate,
    AccountsPayableOut,
    AccountsPayablePaymentCreate,
    AccountsPayableStatusUpdate,
    AccountsPayableUpdate,
)
from app.api.responses import ApiErrorResponse, ApiSuccessResponse, success_response
from app.repositories.accounts_payable_repository import AccountsPayableRepository
from app.services.accounts_payable_service import (
    AccountsPayableService,
)

router = APIRouter(prefix="/accounts-payable", tags=["accounts-payable"])

_repository = AccountsPayableRepository()
_service = AccountsPayableService(
    repository=_repository,
)


def get_accounts_payable_service() -> AccountsPayableService:
    """Retorna a instancia padrao do servico."""

    return _service


ServiceDep = Annotated[AccountsPayableService, Depends(get_accounts_payable_service)]

ERROR_RESPONSES = {
    status.HTTP_404_NOT_FOUND: {"model": ApiErrorResponse, "description": "Recurso nao encontrado."},
    status.HTTP_409_CONFLICT: {"model": ApiErrorResponse, "description": "Regra de negocio violada."},
    status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorResponse, "description": "Erro de validacao."},
}


@router.post(
    "",
    response_model=ApiSuccessResponse[AccountsPayableOut],
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_422_UNPROCESSABLE_ENTITY: ERROR_RESPONSES[status.HTTP_422_UNPROCESSABLE_ENTITY]},
)
def create_accounts_payable(
    payload: AccountsPayableCreate,
    service: ServiceDep,
) -> ApiSuccessResponse[AccountsPayableOut]:
    """Cria uma nova conta a pagar."""

    return success_response(service.create(payload), "Conta a pagar criada com sucesso.")


@router.get(
    "",
    response_model=ApiSuccessResponse[list[AccountsPayableOut]],
    status_code=status.HTTP_200_OK,
)
def list_accounts_payable(service: ServiceDep) -> ApiSuccessResponse[list[AccountsPayableOut]]:
    """Lista as contas a pagar cadastradas."""

    return success_response(service.list(), "Contas a pagar listadas com sucesso.")


@router.get(
    "/overdue",
    response_model=ApiSuccessResponse[list[AccountsPayableOut]],
    status_code=status.HTTP_200_OK,
)
def list_overdue_accounts_payable(service: ServiceDep) -> ApiSuccessResponse[list[AccountsPayableOut]]:
    """Lista as contas a pagar vencidas."""

    return success_response(service.list_overdue(), "Contas a pagar vencidas listadas com sucesso.")


@router.get(
    "/{accounts_payable_id}",
    response_model=ApiSuccessResponse[AccountsPayableOut],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def get_accounts_payable(
    accounts_payable_id: UUID,
    service: ServiceDep,
) -> ApiSuccessResponse[AccountsPayableOut]:
    """Busca uma conta a pagar pelo identificador."""

    return success_response(
        service.get_by_id(accounts_payable_id),
        "Conta a pagar consultada com sucesso.",
    )


@router.put(
    "/{accounts_payable_id}",
    response_model=ApiSuccessResponse[AccountsPayableOut],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
def update_accounts_payable(
    accounts_payable_id: UUID,
    payload: AccountsPayableUpdate,
    service: ServiceDep,
) -> ApiSuccessResponse[AccountsPayableOut]:
    """Atualiza uma conta a pagar existente."""

    return success_response(
        service.update(accounts_payable_id, payload),
        "Conta a pagar atualizada com sucesso.",
    )


@router.post(
    "/{accounts_payable_id}/payment",
    response_model=ApiSuccessResponse[AccountsPayableOut],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
def register_accounts_payable_payment(
    accounts_payable_id: UUID,
    payload: AccountsPayablePaymentCreate,
    service: ServiceDep,
) -> ApiSuccessResponse[AccountsPayableOut]:
    """Registra o pagamento de uma conta a pagar."""

    return success_response(
        service.register_payment(accounts_payable_id, payload),
        "Pagamento registrado com sucesso.",
    )


@router.patch(
    "/{accounts_payable_id}/status",
    response_model=ApiSuccessResponse[AccountsPayableOut],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
def transition_accounts_payable_status(
    accounts_payable_id: UUID,
    payload: AccountsPayableStatusUpdate,
    service: ServiceDep,
) -> ApiSuccessResponse[AccountsPayableOut]:
    """Atualiza o status de uma conta a pagar."""

    return success_response(
        service.transition_status(accounts_payable_id, payload),
        "Status da conta a pagar atualizado com sucesso.",
    )


@router.post(
    "/{accounts_payable_id}/cancel",
    response_model=ApiSuccessResponse[AccountsPayableOut],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
def cancel_accounts_payable(
    accounts_payable_id: UUID,
    service: ServiceDep,
) -> ApiSuccessResponse[AccountsPayableOut]:
    """Cancela uma conta a pagar."""

    return success_response(
        service.cancel(accounts_payable_id),
        "Conta a pagar cancelada com sucesso.",
    )


@router.delete(
    "/{accounts_payable_id}",
    response_model=ApiErrorResponse,
    status_code=status.HTTP_409_CONFLICT,
    responses={
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
        status.HTTP_409_CONFLICT: {
            "model": ApiErrorResponse,
            "description": "Remocao fisica bloqueada para preservar rastreabilidade.",
        },
    },
)
def delete_accounts_payable(
    accounts_payable_id: UUID,
    service: ServiceDep,
) -> ApiErrorResponse:
    """Bloqueia a remocao fisica de uma conta a pagar."""

    service.delete(accounts_payable_id)
