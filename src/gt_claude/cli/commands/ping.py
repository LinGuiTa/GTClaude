import time

from gt_claude import __version__
from gt_claude.core.bus.commands import PingCommand
from gt_claude.core.bus.envelope import JsonRpcRequest
from gt_claude.core.config import load_config
from gt_claude.core.transport.socket_client import send_request


# 向 gt-core 发送 core.ping 请求，并把 daemon 状态打印给用户
async def run_ping() -> int:
    config = load_config()
    started = time.perf_counter()
    command = PingCommand(client=f"gt/{__version__}")
    request = JsonRpcRequest(
        id="cli-ping-1",
        method="core.ping",
        params=command.model_dump(),
    )

    response = await send_request(host=config.host, port=config.port, request=request)
    latency_ms = int((time.perf_counter() - started) * 1000)

    if "error" in response:
        error = response["error"]
        print(f"error code={error['code']} message={error['message']}")
        return 1

    result = response["result"]
    print(
        f"pong server={result['server_version']} "
        f"uptime={result['uptime_ms']}ms "
        f"latency={latency_ms}ms"
    )
    return 0
