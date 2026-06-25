import pytest
from pydantic import ValidationError

from gt_claude.core.bus.envelope import JsonRpcRequest


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
