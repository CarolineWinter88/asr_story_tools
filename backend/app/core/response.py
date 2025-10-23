"""统一响应格式"""
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def error_response(message: str = "操作失败", code: int = 400) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": None
    }


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    total: int
    page: int
    page_size: int
    items: list[T]

