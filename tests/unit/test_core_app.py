import pytest

from gt_claude.core.app import CoreApp


# 功能：验证 CoreApp 的 core.ping handler 会返回 PongResult 形状的 dict
# 设计：直接调用 _handle_ping，不启动 TCP server，让这个测试只关注 daemon 的业务 handler
@pytest.mark.asyncio
async def test_core_app_handle_ping_returns_pong_result() -> None:
    app = CoreApp()

    result = await app._handle_ping({"type": "core.ping", "client": "gt/0.1.0"})

    assert result["server_version"] == "0.1.0"
    assert isinstance(result["uptime_ms"], int)
    assert result["received_at"].endswith("+00:00")
