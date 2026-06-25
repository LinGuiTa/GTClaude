import asyncio
import json
from typing import Any

from gt_claude.core.bus.envelope import JsonRpcRequest


# 连接 gt-core，发送一个 JSON-RPC 请求，并读取一行 JSON 响应
async def send_request(*, host: str, port: int, request: JsonRpcRequest) -> dict[str, Any]:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        # 请求也按 NDJSON 协议发送：一个 JSON 对象 + 一个换行符
        writer.write(request.model_dump_json().encode() + b"\n")
        await writer.drain()

        # S0 的客户端一次只等待一行响应；后续事件流会单独扩展订阅协议
        line = await reader.readline()
    finally:
        # 无论成功还是失败，都关闭客户端连接，避免测试或 CLI 泄漏 socket
        writer.close()
        await writer.wait_closed()

    response = json.loads(line.decode())
    if not isinstance(response, dict):
        raise ValueError("gt-core response must be a JSON object")
    return response
