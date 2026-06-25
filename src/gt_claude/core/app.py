import time
from datetime import UTC, datetime
from typing import Any

from gt_claude import __version__
from gt_claude.core.bus.commands import PingCommand, PongResult
from gt_claude.core.config import load_config
from gt_claude.core.transport.socket_server import SocketServer


class CoreApp:
    def __init__(self) -> None:
        # 启动时读取配置；后续 daemon 会用它决定监听地址和端口
        self.config = load_config()

        # 记录进程启动时间；ping 时用它计算 daemon 已运行多久
        self.started_at = time.perf_counter()

        # gt-core 内部持有一个 SocketServer，负责接收 CLI/TUI 的 JSON-RPC 请求
        self.server = SocketServer(host=self.config.host, port=self.config.port)

    # 处理 core.ping 命令，并返回可放进 JsonRpcSuccess.result 的 dict
    async def _handle_ping(self, params: dict[str, Any]) -> dict[str, Any]:
        PingCommand.model_validate(params)
        uptime_ms = int((time.perf_counter() - self.started_at) * 1000)
        result = PongResult(
            server_version=__version__,
            uptime_ms=uptime_ms,
            received_at=datetime.now(UTC).isoformat(),
        )
        return result.model_dump()
