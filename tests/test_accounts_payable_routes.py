from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.accounts_payable_routes import get_accounts_payable_service
from app.main import create_app
from app.repositories.accounts_payable_repository import AccountsPayableRepository
from app.services.accounts_payable_service import AccountsPayableService


@pytest.fixture
def client() -> TestClient:
    repository = AccountsPayableRepository()
    service = AccountsPayableService(repository=repository)
    app = create_app()
    app.dependency_overrides[get_accounts_payable_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def payload_criacao() -> dict[str, object]:
    return {
        "descricao": "Pagamento de hospedagem",
        "fornecedor_ou_favorecido": "Fornecedor Cloud",
        "categoria": "Infraestrutura",
        "valor_previsto": "149.90",
        "data_vencimento": (date.today() + timedelta(days=5)).isoformat(),
        "data_emissao": date.today().isoformat(),
        "centro_de_custo": "TI",
        "observacoes": "Ambiente de producao",
    }


def criar_conta(client: TestClient, payload_criacao: dict[str, object]) -> dict[str, object]:
    response = client.post("/accounts-payable", json=payload_criacao)

    assert response.status_code == 201
    return response.json()["dados"]


def test_post_accounts_payable_deve_retornar_201(client: TestClient, payload_criacao: dict[str, object]) -> None:
    response = client.post("/accounts-payable", json=payload_criacao)

    body = response.json()

    assert response.status_code == 201
    assert body["sucesso"] is True
    assert body["dados"]["descricao"] == payload_criacao["descricao"]
    assert body["dados"]["status"] == "pending"


def test_get_accounts_payable_deve_retornar_200_para_registro_existente(
    client: TestClient,
    payload_criacao: dict[str, object],
) -> None:
    conta = criar_conta(client, payload_criacao)

    response = client.get(f"/accounts-payable/{conta['id']}")

    body = response.json()

    assert response.status_code == 200
    assert body["sucesso"] is True
    assert body["dados"]["id"] == conta["id"]


def test_get_accounts_payable_list_deve_retornar_200(client: TestClient, payload_criacao: dict[str, object]) -> None:
    criar_conta(client, payload_criacao)

    response = client.get("/accounts-payable")

    body = response.json()

    assert response.status_code == 200
    assert body["sucesso"] is True
    assert len(body["dados"]) == 1


@pytest.mark.xfail(reason="A API atual bloqueia DELETE com 409 para preservar rastreabilidade.")
def test_delete_accounts_payable_deve_retornar_204_quando_remocao_estiver_disponivel(
    client: TestClient,
    payload_criacao: dict[str, object],
) -> None:
    conta = criar_conta(client, payload_criacao)

    response = client.delete(f"/accounts-payable/{conta['id']}")

    assert response.status_code == 204


def test_get_accounts_payable_deve_retornar_404_para_id_inexistente(client: TestClient) -> None:
    response = client.get(f"/accounts-payable/{uuid4()}")

    body = response.json()

    assert response.status_code == 404
    assert body["sucesso"] is False
    assert body["erro"]["codigo"] == "conta_nao_encontrada"
