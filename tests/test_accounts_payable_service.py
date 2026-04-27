from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.accounts_payable import (
    AccountsPayableCreate,
    AccountsPayablePaymentCreate,
    AccountsPayableStatus,
    AccountsPayableStatusUpdate,
    AccountsPayableUpdate,
)
from app.repositories.accounts_payable_repository import AccountsPayableRepository
from app.services.accounts_payable_service import (
    AccountsPayableDeletionBlockedError,
    AccountsPayableInvalidStateError,
    AccountsPayableNotFoundError,
    AccountsPayableService,
)


@pytest.fixture
def repository() -> AccountsPayableRepository:
    return AccountsPayableRepository()


@pytest.fixture
def service(repository: AccountsPayableRepository) -> AccountsPayableService:
    return AccountsPayableService(repository=repository)


@pytest.fixture
def conta_payload() -> AccountsPayableCreate:
    return AccountsPayableCreate(
        descricao="Pagamento mensal de internet",
        fornecedor_ou_favorecido="Fornecedor XPTO",
        categoria="Infraestrutura",
        valor_previsto=Decimal("199.90"),
        data_vencimento=date.today() + timedelta(days=5),
        data_emissao=date.today(),
        centro_de_custo="TI",
        observacoes="Contrato principal",
    )


def criar_conta(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
    **overrides: object,
):
    payload = conta_payload.model_copy(update=overrides)
    return service.create(payload)


def test_create_deve_criar_conta_com_status_pendente(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = service.create(conta_payload)

    assert conta.id is not None
    assert conta.status == AccountsPayableStatus.PENDING
    assert conta.descricao == conta_payload.descricao
    assert conta.valor_previsto == Decimal("199.90")


def test_list_deve_retornar_contas_cadastradas(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)

    contas = service.list()

    assert len(contas) == 1
    assert contas[0].id == conta.id


def test_get_by_id_deve_retornar_conta_existente(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)

    encontrada = service.get_by_id(conta.id)

    assert encontrada.id == conta.id
    assert encontrada.fornecedor_ou_favorecido == "Fornecedor XPTO"


def test_update_deve_atualizar_campos_permitidos(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)

    atualizada = service.update(
        conta.id,
        AccountsPayableUpdate(
            descricao="Pagamento revisado de internet",
            categoria="Servicos",
            valor_previsto=Decimal("249.90"),
        ),
    )

    assert atualizada.descricao == "Pagamento revisado de internet"
    assert atualizada.categoria == "Servicos"
    assert atualizada.valor_previsto == Decimal("249.90")


def test_update_deve_bloquear_conta_cancelada(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)
    service.cancel(conta.id)

    with pytest.raises(AccountsPayableInvalidStateError, match="cancelada nao pode ser atualizada"):
        service.update(conta.id, AccountsPayableUpdate(descricao="Nao pode alterar"))


def test_update_deve_bloquear_conta_paga(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)
    service.register_payment(
        conta.id,
        AccountsPayablePaymentCreate(
            data_pagamento=date.today(),
            valor_pago=conta.valor_previsto,
        ),
    )

    with pytest.raises(AccountsPayableInvalidStateError, match="paga nao pode ser atualizada"):
        service.update(conta.id, AccountsPayableUpdate(descricao="Nao pode alterar"))


def test_register_payment_deve_marcar_conta_como_paga(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)

    paga = service.register_payment(
        conta.id,
        AccountsPayablePaymentCreate(
            data_pagamento=date.today(),
            valor_pago=conta.valor_previsto,
            observacao_pagamento="Pagamento realizado no vencimento",
        ),
    )

    assert paga.status == AccountsPayableStatus.PAID
    assert paga.data_pagamento == date.today()
    assert paga.valor_pago == conta.valor_previsto


def test_register_payment_deve_rejeitar_valor_diferente_do_previsto(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)

    with pytest.raises(AccountsPayableInvalidStateError, match="valor_pago deve ser igual ao valor_previsto"):
        service.register_payment(
            conta.id,
            AccountsPayablePaymentCreate(
                data_pagamento=date.today(),
                valor_pago=Decimal("150.00"),
            ),
        )


def test_register_payment_deve_rejeitar_data_antes_da_emissao(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(
        service,
        conta_payload,
        data_emissao=date.today() - timedelta(days=2),
    )

    with pytest.raises(AccountsPayableInvalidStateError, match="data_pagamento nao pode ser anterior a data_emissao"):
        service.register_payment(
            conta.id,
            AccountsPayablePaymentCreate(
                data_pagamento=date.today() - timedelta(days=3),
                valor_pago=conta.valor_previsto,
            ),
        )


def test_cancel_deve_marcar_conta_como_cancelada(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)

    cancelada = service.cancel(conta.id)

    assert cancelada.status == AccountsPayableStatus.CANCELLED


def test_delete_deve_bloquear_remocao_fisica(
    service: AccountsPayableService,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(service, conta_payload)

    with pytest.raises(AccountsPayableDeletionBlockedError, match="remocao fisica nao e permitida"):
        service.delete(conta.id)


def test_list_overdue_deve_sincronizar_status_vencido(
    service: AccountsPayableService,
    repository: AccountsPayableRepository,
    conta_payload: AccountsPayableCreate,
) -> None:
    conta = criar_conta(
        service,
        conta_payload,
        data_vencimento=date.today() - timedelta(days=1),
        data_emissao=date.today() - timedelta(days=2),
    )

    vencidas = service.list_overdue()
    persistida = repository.get_by_id(conta.id)

    assert len(vencidas) == 1
    assert vencidas[0].id == conta.id
    assert vencidas[0].status == AccountsPayableStatus.OVERDUE
    assert persistida is not None
    assert persistida.status == AccountsPayableStatus.OVERDUE


@pytest.mark.parametrize(
    ("operation", "expected_exception"),
    [
        ("get", AccountsPayableNotFoundError),
        ("update", AccountsPayableNotFoundError),
        ("payment", AccountsPayableNotFoundError),
        ("status", AccountsPayableNotFoundError),
        ("cancel", AccountsPayableNotFoundError),
        ("delete", AccountsPayableNotFoundError),
    ],
)
def test_operacoes_devem_falhar_quando_id_nao_existir(
    service: AccountsPayableService,
    operation: str,
    expected_exception: type[Exception],
) -> None:
    conta_id_inexistente = uuid4()

    with pytest.raises(expected_exception, match="nao encontrada"):
        if operation == "get":
            service.get_by_id(conta_id_inexistente)
        elif operation == "update":
            service.update(
                conta_id_inexistente,
                AccountsPayableUpdate(descricao="Atualizacao inexistente"),
            )
        elif operation == "payment":
            service.register_payment(
                conta_id_inexistente,
                AccountsPayablePaymentCreate(
                    data_pagamento=date.today(),
                    valor_pago=Decimal("199.90"),
                ),
            )
        elif operation == "status":
            service.transition_status(
                conta_id_inexistente,
                AccountsPayableStatusUpdate(status=AccountsPayableStatus.CANCELLED),
            )
        elif operation == "cancel":
            service.cancel(conta_id_inexistente)
        elif operation == "delete":
            service.delete(conta_id_inexistente)
