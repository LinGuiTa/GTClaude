import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from gt_claude.core.bus.envelope import (
    METHOD_NOT_FOUND,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcSuccess,
    make_error,
)

# Handler 是 daemon 内部处理某个 method 的异步函数
Handler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class SocketServer:
    def __init__(self, *, host: str, port: int) -> None:
        # 监听地址；S0 默认是 127.0.0.1，只接受本机连接
        self.host = host

        # 监听端口；测试里传 0 表示让操作系统自动分配空闲端口
        self.port = port

        # 实际绑定端口；当 port=0 时，start 后才能知道系统分配了哪个端口
        self.bound_port: int | None = None

        # asyncio 底层 TCP server 对象；stop 时需要用它关闭监听
        self._server: asyncio.Server | None = None

        # method -> handler 的路由表；例如 core.ping -> _handle_ping
        self._handlers: dict[str, Handler] = {}

    # 注册某个 JSON-RPC method 对应的处理函数
    def register(self, method: str, handler: Handler) -> None:
        self._handlers[method] = handler

    # 启动 TCP server，开始监听客户端连接
    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        socket = self._server.sockets[0]
        self.bound_port = int(socket.getsockname()[1])

    # 停止 TCP server，释放监听端口
    async def stop(self) -> None:
        if self._server is None:
            return
        self._server.close()
        await self._server.wait_closed()
        self._server = None

    # 处理一个客户端连接；S0 先支持客户端发送一行或多行 NDJSON 请求
    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        try:
            while line := await reader.readline():
                response = await self._dispatch_line(line)
                writer.write(response.model_dump_json().encode() + b"\n")
                await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    # 分发一行 JSON-RPC 请求到对应 handler，并包装成响应 envelope
    async def _dispatch_line(self, line: bytes) -> JsonRpcSuccess | JsonRpcError:
        raw = json.loads(line.decode())
        request = JsonRpcRequest.model_validate(raw)
        handler = self._handlers.get(request.method)
        if handler is None:
            return make_error(
                id=request.id,
                code=METHOD_NOT_FOUND,
                message=f"method not found: {request.method}",
            )

        result = await handler(request.params)
        return JsonRpcSuccess(id=request.id, result=result)
