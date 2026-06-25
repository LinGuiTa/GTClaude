import asyncio
import json
from typing import Any

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
