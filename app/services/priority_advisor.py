from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Final
from urllib import error, request

from app.models.accounts_payable import AccountsPayablePriority, AccountsPayableStatus

_OPENAI_URL: Final[str] = "https://api.openai.com/v1/responses"
_DEFAULT_MODEL: Final[str] = "gpt-4o-mini"
_DEFAULT_TIMEOUT_SECONDS: Final[float] = 5.0


@dataclass(slots=True)
class PriorityAdvisor:
    """Sugere prioridade com heuristica local e fallback seguro."""

    api_key: str | None = None
    model: str = _DEFAULT_MODEL
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")

        model = os.getenv("OPENAI_MODEL")
        if model:
            self.model = model

    def suggest_priority(
        self,
        *,
        title: str,
        description: str | None,
        due_date: date | None,
        status: AccountsPayableStatus,
    ) -> AccountsPayablePriority:
        """Retorna prioridade sugerida com fallback obrigatorio."""

        local_priority = self._suggest_local_priority(
            title=title,
            description=description,
            due_date=due_date,
            status=status,
        )

        if not self.api_key:
            return local_priority

        remote_priority = self._suggest_llm_priority(
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            fallback=local_priority,
        )
        return remote_priority or local_priority

    def _suggest_local_priority(
        self,
        *,
        title: str,
        description: str | None,
        due_date: date | None,
        status: AccountsPayableStatus,
    ) -> AccountsPayablePriority:
        """Aplica heuristica local sem custo externo."""

        if status == AccountsPayableStatus.CANCELLED:
            return AccountsPayablePriority.LOW

        if status == AccountsPayableStatus.PAID:
            return AccountsPayablePriority.LOW

        if status == AccountsPayableStatus.OVERDUE:
            return AccountsPayablePriority.CRITICAL

        text = f"{title} {description or ''}".lower()
        today = datetime.now(UTC).date()

        if due_date is not None:
            days_until_due = (due_date - today).days
            if days_until_due < 0:
                return AccountsPayablePriority.CRITICAL
            if days_until_due <= 1:
                return AccountsPayablePriority.HIGH
            if days_until_due <= 3:
                return AccountsPayablePriority.MEDIUM
        else:
            days_until_due = None

        urgent_terms = (
            "urgente",
            "hoje",
            "imediato",
            "critico",
            "crítico",
            "vencido",
            "bloqueio",
            "multa",
            "juros",
            "fornecedor",
        )
        important_terms = (
            "pagamento",
            "aprovacao",
            "aprovação",
            "nota fiscal",
            "boleto",
            "contrato",
        )

        if any(term in text for term in urgent_terms):
            return AccountsPayablePriority.HIGH

        if any(term in text for term in important_terms):
            return AccountsPayablePriority.MEDIUM

        if days_until_due is not None and days_until_due <= 7:
            return AccountsPayablePriority.MEDIUM

        return AccountsPayablePriority.LOW

    def _suggest_llm_priority(
        self,
        *,
        title: str,
        description: str | None,
        due_date: date | None,
        status: AccountsPayableStatus,
        fallback: AccountsPayablePriority,
    ) -> AccountsPayablePriority | None:
        """Consulta LLM com timeout curto e retorno restrito."""

        try:
            payload = self._build_payload(
                title=title,
                description=description,
                due_date=due_date,
                status=status,
                fallback=fallback,
            )
            http_request = request.Request(
                _OPENAI_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except (TimeoutError, error.URLError, error.HTTPError, OSError, ValueError):
            return None

        try:
            response_data = json.loads(body)
            raw_output = self._extract_output_text(response_data)
            if raw_output is None:
                return None
            normalized_output = raw_output.strip().strip('"').strip().lower()
            return AccountsPayablePriority(normalized_output)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return None

    def _build_payload(
        self,
        *,
        title: str,
        description: str | None,
        due_date: date | None,
        status: AccountsPayableStatus,
        fallback: AccountsPayablePriority,
    ) -> dict[str, object]:
        """Monta payload restrito para a chamada remota."""

        instructions = (
            "Voce recebe dados de uma conta a pagar interna. "
            "Responda com apenas uma palavra em minusculas: "
            "low, medium, high ou critical. "
            "Considere urgencia, vencimento e impacto operacional. "
            f"Se houver ambiguidade, responda {fallback.value}."
        )
        task_context = {
            "title": title,
            "description": description,
            "due_date": due_date.isoformat() if due_date else None,
            "status": status.value,
        }

        return {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": instructions}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": json.dumps(task_context, ensure_ascii=True),
                        }
                    ],
                },
            ],
            "max_output_tokens": 8,
        }

    def _extract_output_text(self, response_data: dict[str, object]) -> str | None:
        """Extrai texto do retorno da API de respostas."""

        output = response_data.get("output")
        if not isinstance(output, list):
            return response_data.get("output_text") if isinstance(response_data.get("output_text"), str) else None

        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text

        output_text = response_data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text

        return None
