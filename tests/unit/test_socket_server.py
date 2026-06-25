import asyncio
import json
from typing import Any

from gt_claude.core.bus.envelope import INVALID_REQUEST, METHOD_NOT_FOUND
from gt_claude.core.transport.socket_server import SocketServer


# 功能：验证 SocketServer 能把一行 JSON-RPC 请求分发给已注册的 handler
# 设计：启动真实 TCP server 并通过 asyncio.open_connection 发送 NDJSON，覆盖最小传输链路
def test_socket_server_dispatches_registered_method() -> None:
    async def scenario() -> None:
        server = SocketServer(host="127.0.0.1", port=0)

        async def echo_handler(params: dict[str, Any]) -> dict[str, Any]:
            return {"echo": params["value"]}

        server.register("test.echo", echo_handler)
        await server.start()
        assert server.bound_port is not None

        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", server.bound_port)
            writer.write(
                b'{"jsonrpc":"2.0","id":"u-1","method":"test.echo","params":{"value":"ok"}}\n'
            )
            await writer.drain()
            line = await reader.readline()
            writer.close()
            await writer.wait_closed()
        finally:
            await server.stop()

        response = json.loads(line.decode())
        assert response == {"jsonrpc": "2.0", "id": "u-1", "result": {"echo": "ok"}}

    asyncio.run(scenario())


# 功能：验证未注册 method 会返回 JSON-RPC METHOD_NOT_FOUND 错误，而不是让 server 崩掉
# 设计：启动真实 TCP server 但不注册 missing.method，覆盖 daemon 最常见的路由失败场景
def test_socket_server_returns_method_not_found_for_unknown_method() -> None:
    async def scenario() -> None:
        server = SocketServer(host="127.0.0.1", port=0)
        await server.start()
        assert server.bound_port is not None

        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", server.bound_port)
            writer.write(
                b'{"jsonrpc":"2.0","id":"u-404","method":"missing.method","params":{}}\n'
            )
            await writer.drain()
            line = await reader.readline()
            writer.close()
            await writer.wait_closed()
        finally:
            await server.stop()

        response = json.loads(line.decode())
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "u-404"
        assert response["error"]["code"] == METHOD_NOT_FOUND
        assert response["error"]["message"] == "method not found: missing.method"

    asyncio.run(scenario())


# 功能：验证客户端发送非法 JSON 时，server 返回 INVALID_REQUEST 错误
# 设计：直接发送 not-json 换行，覆盖网络层最早可能遇到的输入格式错误
def test_socket_server_returns_invalid_request_for_malformed_json() -> None:
    async def scenario() -> None:
        server = SocketServer(host="127.0.0.1", port=0)
        await server.start()
        assert server.bound_port is not None

        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", server.bound_port)
            writer.write(b"not-json\n")
            await writer.drain()
            line = await reader.readline()
            writer.close()
            await writer.wait_closed()
        finally:
            await server.stop()

        response = json.loads(line.decode())
        assert response["jsonrpc"] == "2.0"
        assert response["id"] is None
        assert response["error"]["code"] == INVALID_REQUEST

    asyncio.run(scenario())
