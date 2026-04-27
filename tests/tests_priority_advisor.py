from __future__ import annotations

from datetime import date, timedelta
from urllib import error

import pytest

from app.models.accounts_payable import AccountsPayablePriority, AccountsPayableStatus
from app.services import priority_advisor as priority_advisor_module
from app.services.priority_advisor import PriorityAdvisor


@pytest.fixture
def advisor() -> PriorityAdvisor:
    return PriorityAdvisor(api_key=None)


def test_suggest_priority_deve_retornar_low_quando_conta_estiver_sem_urgencia(
    advisor: PriorityAdvisor,
) -> None:
    prioridade = advisor.suggest_priority(
        descricao="Conta administrativa recorrente",
        observacoes="Processamento mensal interno",
        data_vencimento=date.today() + timedelta(days=15),
        status=AccountsPayableStatus.PENDING,
    )

    assert prioridade == AccountsPayablePriority.LOW


def test_suggest_priority_deve_retornar_medium_quando_houver_indicio_importante(
    advisor: PriorityAdvisor,
) -> None:
    prioridade = advisor.suggest_priority(
        descricao="Pagamento de boleto do escritorio",
        observacoes="Necessita conciliacao posterior",
        data_vencimento=date.today() + timedelta(days=10),
        status=AccountsPayableStatus.PENDING,
    )

    assert prioridade == AccountsPayablePriority.MEDIUM


def test_suggest_priority_deve_retornar_high_quando_vencimento_estiver_proximo(
    advisor: PriorityAdvisor,
) -> None:
    prioridade = advisor.suggest_priority(
        descricao="Renovacao de contrato de servico",
        observacoes="Pagamento precisa ocorrer hoje",
        data_vencimento=date.today() + timedelta(days=1),
        status=AccountsPayableStatus.PENDING,
    )

    assert prioridade == AccountsPayablePriority.HIGH


def test_suggest_priority_deve_fazer_fallback_para_heuristica_local_quando_chamada_externa_falhar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    advisor = PriorityAdvisor(api_key="token-de-teste")

    def fake_urlopen(*args, **kwargs):
        raise error.URLError("falha simulada")

    monkeypatch.setattr(priority_advisor_module.request, "urlopen", fake_urlopen)

    prioridade = advisor.suggest_priority(
        descricao="Conta vencida de fornecedor critico",
        observacoes="Aplicacao de multa por atraso",
        data_vencimento=date.today() - timedelta(days=1),
        status=AccountsPayableStatus.PENDING,
    )

    assert prioridade == AccountsPayablePriority.CRITICAL
