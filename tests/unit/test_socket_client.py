from typing import Any

import pytest

from gt_claude.core.bus.envelope import JsonRpcRequest
from gt_claude.core.transport.socket_client import send_request
from gt_claude.core.transport.socket_server import SocketServer


# 功能：验证 send_request 能连接 SocketServer，发送 JSON-RPC 请求并读回响应
# 设计：复用真实 SocketServer，而不是 mock 网络层，确保客户端和服务端协议真正能互通
@pytest.mark.asyncio
async def test_send_request_roundtrips_with_socket_server() -> None:
    server = SocketServer(host="127.0.0.1", port=0)

    async def echo_handler(params: dict[str, Any]) -> dict[str, Any]:
        return {"echo": params["value"]}

    server.register("test.echo", echo_handler)
    await server.start()
    assert server.bound_port is not None

    try:
        response = await send_request(
            host="127.0.0.1",
            port=server.bound_port,
            request=JsonRpcRequest(
                id="u-1",
                method="test.echo",
                params={"value": "ok"},
            ),
        )
    finally:
        await server.stop()

    assert response == {"jsonrpc": "2.0", "id": "u-1", "result": {"echo": "ok"}}
