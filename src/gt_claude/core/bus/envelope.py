from typing import Any, Literal

from pydantic import BaseModel, Field

# JSON-RPC 2.0 标准错误码：请求对象格式不合法
INVALID_REQUEST = -32600

# JSON-RPC 2.0 标准错误码：请求的 method 没有注册 handler
METHOD_NOT_FOUND = -32601


class JsonRpcRequest(BaseModel):
    # JSON-RPC 固定协议版本；客户端和 daemon 都用它确认消息属于 JSON-RPC 2.0
    jsonrpc: Literal["2.0"] = "2.0"

    # 请求 ID；客户端用它把请求和响应对应起来
    id: str

    # 方法名；daemon 根据它决定把请求分发给哪个 handler
    method: str = Field(min_length=1)

    # 请求参数；不同 method 会有不同参数，所以这里先用通用 dict 承载
    params: dict[str, Any] = Field(default_factory=dict)


class JsonRpcSuccess(BaseModel):
    # JSON-RPC 固定协议版本；成功响应也必须标明协议版本
    jsonrpc: Literal["2.0"] = "2.0"

    # 请求 ID；必须和请求里的 id 一致，客户端靠它匹配响应
    id: str

    # 成功结果；不同 method 的 result 结构不同，所以先用通用 dict 承载
    result: dict[str, Any]


class JsonRpcErrorBody(BaseModel):
    # 标准错误码；例如 -32601 表示 method not found
    code: int

    # 给人看的错误信息；CLI 可以直接打印它帮助用户理解失败原因
    message: str

    # 可选调试数据；S0 暂时不用，但保留 JSON-RPC 标准扩展位置
    data: dict[str, Any] | None = None


class JsonRpcError(BaseModel):
    # JSON-RPC 固定协议版本；错误响应也必须标明协议版本
    jsonrpc: Literal["2.0"] = "2.0"

    # 请求 ID；如果请求本身无法解析，可能没有 ID，所以允许 None
    id: str | None

    # 错误正文；里面包含 code/message/data
    error: JsonRpcErrorBody


# 创建标准 JSON-RPC 错误响应，避免每个调用点手写重复结构
def make_error(
    *,
    id: str | None,
    code: int,
    message: str,
    data: dict[str, Any] | None = None,
) -> JsonRpcError:
    return JsonRpcError(
        id=id,
        error=JsonRpcErrorBody(code=code, message=message, data=data),
    )
