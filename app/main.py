from __future__ import annotations

import os
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.accounts_payable_routes import router as accounts_payable_router
from app.api.responses import ApiErrorBody, ApiErrorResponse, ApiValidationDetail, success_response
from app.services.accounts_payable_service import (
    AccountsPayableDeletionBlockedError,
    AccountsPayableInvalidStateError,
    AccountsPayableNotFoundError,
)


def create_app() -> FastAPI:
    """Cria a instancia principal da micro-API."""

    app = FastAPI(
        title=os.getenv("APP_NAME", "Micro-API de Contas a Pagar"),
        version=os.getenv("APP_VERSION", "0.1.0"),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    api_prefix = os.getenv("API_PREFIX", "")

    app.include_router(accounts_payable_router, prefix=api_prefix)

    @app.get("/", tags=["health"])
    def read_root() -> dict[str, Any]:
        """Retorna um status simples da aplicacao."""

        return success_response(
            {
                "nome": app.title,
                "versao": app.version,
                "status": "online",
            },
            "Aplicacao inicializada com sucesso.",
        ).model_dump(mode="json")

    @app.exception_handler(AccountsPayableNotFoundError)
    async def handle_not_found(_: Request, exc: AccountsPayableNotFoundError) -> JSONResponse:
        return _error_response(HTTPStatus.NOT_FOUND, "conta_nao_encontrada", str(exc))

    @app.exception_handler(AccountsPayableInvalidStateError)
    async def handle_invalid_state(_: Request, exc: AccountsPayableInvalidStateError) -> JSONResponse:
        return _error_response(HTTPStatus.CONFLICT, "estado_invalido", str(exc))

    @app.exception_handler(AccountsPayableDeletionBlockedError)
    async def handle_delete_blocked(
        _: Request,
        exc: AccountsPayableDeletionBlockedError,
    ) -> JSONResponse:
        return _error_response(HTTPStatus.CONFLICT, "remocao_fisica_bloqueada", str(exc))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            ApiValidationDetail(
                campo=".".join(str(part) for part in error["loc"] if part != "body"),
                mensagem=error["msg"],
            )
            for error in exc.errors()
        ]
        return _error_response(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "erro_validacao",
            "Os dados informados sao invalidos.",
            details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        status_phrase = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")
        detail = exc.detail if isinstance(exc.detail, str) else "Falha ao processar requisicao."
        return _error_response(exc.status_code, status_phrase, detail)

    return app


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[ApiValidationDetail] | None = None,
) -> JSONResponse:
    """Monta uma resposta de erro padronizada."""

    payload = ApiErrorResponse(
        erro=ApiErrorBody(
            codigo=code,
            mensagem=message,
            detalhes=details,
        )
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


app = create_app()
