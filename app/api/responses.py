from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiValidationDetail(BaseModel):
    """Representa um erro de validacao de campo."""

    campo: str = Field(..., description="Caminho do campo com erro.")
    mensagem: str = Field(..., description="Mensagem objetiva de validacao.")


class ApiErrorBody(BaseModel):
    """Representa o corpo padrao de erro da API."""

    codigo: str = Field(..., description="Codigo interno do erro.")
    mensagem: str = Field(..., description="Mensagem objetiva de erro.")
    detalhes: list[ApiValidationDetail] | None = Field(
        default=None,
        description="Detalhes adicionais do erro, quando houver.",
    )


class ApiErrorResponse(BaseModel):
    """Envelope padronizado de erro."""

    sucesso: bool = Field(default=False, description="Indica falha na operacao.")
    erro: ApiErrorBody = Field(..., description="Dados do erro ocorrido.")


class ApiSuccessResponse(BaseModel, Generic[DataT]):
    """Envelope padronizado de sucesso."""

    sucesso: bool = Field(default=True, description="Indica sucesso na operacao.")
    mensagem: str = Field(..., description="Resumo curto do resultado.")
    dados: DataT = Field(..., description="Payload principal da resposta.")


def success_response(data: DataT, message: str) -> ApiSuccessResponse[DataT]:
    """Cria uma resposta padronizada de sucesso."""

    return ApiSuccessResponse[DataT](mensagem=message, dados=data)
