"""Casos de integracao do ciclo de contas a pagar.

Gerados a partir dos prompts da Unidade III, depois ancorados no contrato
real da API (envelope, rotas e regras de estado). Cada caso atravessa o
cliente HTTP, a rota, o servico e o repositorio em memoria, e confere o
efeito na chamada seguinte.

Registro do experimento: docs/forum-unidade-iii-testes-integracao/README.md
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
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


def _payload(**overrides: object) -> dict[str, object]:
    dados: dict[str, object] = {
        "descricao": "Licenca de software financeiro",
        "fornecedor_ou_favorecido": "Fornecedor Cloud",
        "categoria": "Software",
        "valor_previsto": "299.90",
        "data_vencimento": (date.today() + timedelta(days=10)).isoformat(),
        "data_emissao": date.today().isoformat(),
        "centro_de_custo": "TI",
        "observacoes": "Fluxo de integracao",
    }
    dados.update(overrides)
    return dados


def _criar(client: TestClient, **overrides: object) -> dict[str, object]:
    response = client.post("/accounts-payable", json=_payload(**overrides))

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["sucesso"] is True
    return body["dados"]


def _pagamento(valor: str = "299.90", dias_atras: int = 0) -> dict[str, str]:
    return {
        "data_pagamento": (date.today() - timedelta(days=dias_atras)).isoformat(),
        "valor_pago": valor,
        "observacao_pagamento": "Liquidacao integral",
    }


def _como_decimal(valor: object) -> Decimal:
    return Decimal(str(valor))


def test_int01_cadastro_fica_visivel_na_consulta_e_na_listagem(client: TestClient) -> None:
    criada = _criar(client)

    consulta = client.get(f"/accounts-payable/{criada['id']}")
    listagem = client.get("/accounts-payable")

    assert consulta.status_code == 200
    assert consulta.json()["dados"]["id"] == criada["id"]
    assert consulta.json()["dados"]["status"] == "pending"
    assert listagem.status_code == 200
    assert listagem.json()["sucesso"] is True
    assert [item["id"] for item in listagem.json()["dados"]] == [criada["id"]]


def test_int02_atualizacao_permanece_na_consulta_seguinte(client: TestClient) -> None:
    criada = _criar(client)

    atualizacao = client.put(
        f"/accounts-payable/{criada['id']}",
        json={"descricao": "Licenca renegociada com o fornecedor"},
    )
    consulta = client.get(f"/accounts-payable/{criada['id']}")

    assert atualizacao.status_code == 200
    assert atualizacao.json()["dados"]["descricao"] == "Licenca renegociada com o fornecedor"
    assert consulta.status_code == 200
    assert consulta.json()["dados"]["descricao"] == "Licenca renegociada com o fornecedor"
    assert consulta.json()["dados"]["status"] == "pending"
    assert _como_decimal(consulta.json()["dados"]["valor_previsto"]) == Decimal("299.90")


def test_int03_vencimento_aparece_na_listagem_de_overdue_e_na_consulta(client: TestClient) -> None:
    criada = _criar(
        client,
        data_emissao=(date.today() - timedelta(days=5)).isoformat(),
        data_vencimento=(date.today() - timedelta(days=2)).isoformat(),
    )

    vencidas = client.get("/accounts-payable/overdue")
    consulta = client.get(f"/accounts-payable/{criada['id']}")

    assert vencidas.status_code == 200
    assert [item["id"] for item in vencidas.json()["dados"]] == [criada["id"]]
    assert vencidas.json()["dados"][0]["status"] == "overdue"
    assert consulta.json()["dados"]["status"] == "overdue"


def test_int04_pagamento_integral_liquida_remove_de_overdue_e_bloqueia_novo_pagamento(
    client: TestClient,
) -> None:
    criada = _criar(
        client,
        data_emissao=(date.today() - timedelta(days=5)).isoformat(),
        data_vencimento=(date.today() - timedelta(days=2)).isoformat(),
    )

    pagamento = client.post(
        f"/accounts-payable/{criada['id']}/payment",
        json=_pagamento(),
    )
    consulta = client.get(f"/accounts-payable/{criada['id']}")
    vencidas = client.get("/accounts-payable/overdue")
    segundo_pagamento = client.post(
        f"/accounts-payable/{criada['id']}/payment",
        json=_pagamento(),
    )

    assert pagamento.status_code == 200
    assert pagamento.json()["dados"]["status"] == "paid"
    assert consulta.json()["dados"]["status"] == "paid"
    assert consulta.json()["dados"]["data_pagamento"] == date.today().isoformat()
    assert _como_decimal(consulta.json()["dados"]["valor_pago"]) == Decimal("299.90")
    assert vencidas.json()["dados"] == []
    assert segundo_pagamento.status_code == 409
    assert segundo_pagamento.json()["sucesso"] is False
    assert segundo_pagamento.json()["erro"]["codigo"] == "estado_invalido"
    assert client.get(f"/accounts-payable/{criada['id']}").json()["dados"]["status"] == "paid"


def test_int05_cancelamento_bloqueia_atualizacao_e_pagamento(client: TestClient) -> None:
    criada = _criar(client)

    cancelamento = client.post(f"/accounts-payable/{criada['id']}/cancel")
    atualizacao = client.put(
        f"/accounts-payable/{criada['id']}",
        json={"descricao": "Tentativa apos o cancelamento"},
    )
    pagamento = client.post(
        f"/accounts-payable/{criada['id']}/payment",
        json=_pagamento(),
    )
    consulta = client.get(f"/accounts-payable/{criada['id']}")

    assert cancelamento.status_code == 200
    assert cancelamento.json()["dados"]["status"] == "cancelled"
    assert atualizacao.status_code == 409
    assert atualizacao.json()["erro"]["codigo"] == "estado_invalido"
    assert pagamento.status_code == 409
    assert pagamento.json()["erro"]["codigo"] == "estado_invalido"
    assert consulta.json()["dados"]["status"] == "cancelled"
    assert consulta.json()["dados"]["descricao"] == criada["descricao"]


@pytest.mark.parametrize(
    ("metodo", "caminho", "corpo"),
    [
        ("get", "", None),
        ("post", "/payment", "pagamento"),
        ("post", "/cancel", None),
        ("delete", "", None),
    ],
)
def test_int06_operacoes_em_id_inexistente_retornam_404(
    client: TestClient,
    metodo: str,
    caminho: str,
    corpo: str | None,
) -> None:
    url = f"/accounts-payable/{uuid4()}{caminho}"
    kwargs = {"json": _pagamento()} if corpo == "pagamento" else {}

    response = getattr(client, metodo)(url, **kwargs)
    body = response.json()

    assert response.status_code == 404
    assert body["sucesso"] is False
    assert body["erro"]["codigo"] == "conta_nao_encontrada"


@pytest.mark.parametrize(
    "payload",
    [
        _payload(valor_previsto="0.00"),
        {**_payload(), "prioridade": "high"},
        {chave: valor for chave, valor in _payload().items() if chave != "descricao"},
    ],
)
def test_int07_criacao_fora_do_contrato_retorna_422_e_nao_grava(
    client: TestClient,
    payload: dict[str, object],
) -> None:
    response = client.post("/accounts-payable", json=payload)
    listagem = client.get("/accounts-payable")

    assert response.status_code == 422
    assert response.json()["sucesso"] is False
    assert response.json()["erro"]["codigo"] == "erro_validacao"
    assert response.json()["erro"]["detalhes"]
    assert listagem.json()["dados"] == []


def test_int07_rotas_de_estado_rejeitam_contrato_invalido_sem_liquidar(client: TestClient) -> None:
    criada = _criar(client)

    status_pago = client.patch(
        f"/accounts-payable/{criada['id']}/status",
        json={"status": "paid"},
    )
    pagamento_futuro = client.post(
        f"/accounts-payable/{criada['id']}/payment",
        json={
            "data_pagamento": (date.today() + timedelta(days=1)).isoformat(),
            "valor_pago": "299.90",
        },
    )
    consulta = client.get(f"/accounts-payable/{criada['id']}")

    assert status_pago.status_code == 422
    assert status_pago.json()["erro"]["codigo"] == "erro_validacao"
    assert pagamento_futuro.status_code == 422
    assert pagamento_futuro.json()["erro"]["codigo"] == "erro_validacao"
    assert consulta.json()["dados"]["status"] == "pending"
    assert consulta.json()["dados"]["valor_pago"] is None


def test_int08_regras_de_liquidacao_retornam_409_sem_alterar_status(client: TestClient) -> None:
    criada = _criar(
        client,
        data_emissao=date.today().isoformat(),
        data_vencimento=(date.today() + timedelta(days=10)).isoformat(),
    )

    valor_divergente = client.post(
        f"/accounts-payable/{criada['id']}/payment",
        json=_pagamento(valor="150.00"),
    )
    data_anterior = client.post(
        f"/accounts-payable/{criada['id']}/payment",
        json=_pagamento(dias_atras=1),
    )
    consulta = client.get(f"/accounts-payable/{criada['id']}")

    assert valor_divergente.status_code == 409
    assert valor_divergente.json()["erro"]["codigo"] == "estado_invalido"
    assert data_anterior.status_code == 409
    assert data_anterior.json()["erro"]["codigo"] == "estado_invalido"
    assert consulta.json()["dados"]["status"] == "pending"
    assert consulta.json()["dados"]["data_pagamento"] is None
    assert consulta.json()["dados"]["valor_pago"] is None


def test_int09_delete_bloqueado_preserva_a_conta(client: TestClient) -> None:
    criada = _criar(client)

    remocao = client.delete(f"/accounts-payable/{criada['id']}")
    consulta = client.get(f"/accounts-payable/{criada['id']}")

    assert remocao.status_code == 409
    assert remocao.json()["sucesso"] is False
    assert remocao.json()["erro"]["codigo"] == "remocao_fisica_bloqueada"
    assert consulta.status_code == 200
    assert consulta.json()["dados"]["id"] == criada["id"]
    assert consulta.json()["dados"]["status"] == "pending"


def test_int10_conta_vencida_nao_retorna_para_pending(client: TestClient) -> None:
    criada = _criar(
        client,
        data_emissao=(date.today() - timedelta(days=5)).isoformat(),
        data_vencimento=(date.today() - timedelta(days=2)).isoformat(),
    )

    retorno = client.patch(
        f"/accounts-payable/{criada['id']}/status",
        json={"status": "pending"},
    )
    consulta = client.get(f"/accounts-payable/{criada['id']}")

    assert retorno.status_code == 409
    assert retorno.json()["erro"]["codigo"] == "estado_invalido"
    assert consulta.json()["dados"]["status"] == "overdue"
