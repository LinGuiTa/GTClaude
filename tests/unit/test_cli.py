import pytest

from gt_claude.cli.main import async_main
from gt_claude.core.bus.envelope import JsonRpcRequest


# 功能：验证 gt --version 会打印当前 CLI 版本并返回成功状态码
# 设计：直接调用 async_main，避免启动子进程，让这个测试只关注 CLI 参数路由本身
@pytest.mark.asyncio
async def test_cli_version_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = await async_main(["--version"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "gt 0.1.0\n"


# 功能：验证 gt ping 会构造 core.ping 请求，调用 socket client，并打印 daemon 返回值
# 设计：用 monkeypatch 替代真实网络连接，让这个测试只关注 CLI 参数路由和输出格式
@pytest.mark.asyncio
async def test_cli_ping_prints_pong(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured_request: JsonRpcRequest | None = None

    async def fake_send_request(
        *,
        host: str,
        port: int,
        request: JsonRpcRequest,
    ) -> dict[str, object]:
        nonlocal captured_request
        captured_request = request
        assert host == "127.0.0.1"
        assert port == 7437
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "server_version": "0.1.0",
                "uptime_ms": 12,
                "received_at": "2026-06-25T00:00:00+00:00",
            },
        }

    monkeypatch.setattr("gt_claude.cli.commands.ping.send_request", fake_send_request)

    exit_code = await async_main(["ping"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert output.startswith("pong server=0.1.0 uptime=12ms latency=")
    assert captured_request is not None
    assert captured_request.method == "core.ping"
    assert captured_request.params == {"type": "core.ping", "client": "gt/0.1.0"}
