from typing import Any, Literal

from pydantic import BaseModel, Field


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
