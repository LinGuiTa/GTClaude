import pytest
from pydantic import ValidationError

from gt_claude.core.bus.envelope import (
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcSuccess,
    make_error,
)


# 功能：验证 JSON-RPC 请求模型会保存协议版本、请求 ID、方法名和参数
# 设计：用 core.ping 作为最小请求，因为 ping 是 CLI 和 daemon 之间最先跑通的命令
def test_json_rpc_request_keeps_basic_fields() -> None:
    request = JsonRpcRequest(
        id="u-1",
        method="core.ping",
        params={"client": "gt/0.1.0"},
    )

    assert request.jsonrpc == "2.0"
    assert request.id == "u-1"
    assert request.method == "core.ping"
    assert request.params == {"client": "gt/0.1.0"}


# 功能：验证 method 不能为空字符串
# 设计：method 是 daemon 路由命令的关键字段，空 method 不应该进入 socket 分发层

def test_json_rpc_request_rejects_empty_method() -> None:
    with pytest.raises(ValidationError):
        JsonRpcRequest(id="u-1", method="", params={})


# 功能：验证 JSON-RPC 成功响应模型会保存请求 ID 和业务结果
# 设计：用 ping 未来会返回的 server_version 作为最小 result，说明响应和请求通过 id 对应
def test_json_rpc_success_keeps_result() -> None:
    response = JsonRpcSuccess(
        id="u-1",
        result={"server_version": "0.1.0"},
    )

    assert response.jsonrpc == "2.0"
    assert response.id == "u-1"
    assert response.result == {"server_version": "0.1.0"}


# 功能：验证 make_error 能生成标准 JSON-RPC 错误响应
# 设计：用未知 method 的错误码，因为这是 socket server 最早会遇到的真实错误场景
def test_make_error_creates_json_rpc_error_response() -> None:
    response = make_error(
        id="u-404",
        code=METHOD_NOT_FOUND,
        message="method not found: missing.method",
    )

    assert isinstance(response, JsonRpcError)
    assert response.jsonrpc == "2.0"
    assert response.id == "u-404"
    assert response.error.code == METHOD_NOT_FOUND
    assert response.error.message == "method not found: missing.method"
    assert response.error.data is None


# 功能：验证 S0 要用到的 JSON-RPC 错误码不会被误改
# 设计：错误码是 wire protocol 的一部分，客户端和 daemon 必须对这些数字有共同理解
def test_json_rpc_error_code_constants() -> None:
    assert INVALID_REQUEST == -32600
    assert METHOD_NOT_FOUND == -32601
