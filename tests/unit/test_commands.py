from gt_claude.core.bus.commands import PingCommand, PongResult


# 功能：验证 PingCommand 会保存客户端名称，并自动带上 core.ping 类型
# 设计：core.ping 是 GTClaude 的第一条命令，用它建立“命令参数对象”的基本形状
def test_ping_command_keeps_client_and_default_type() -> None:
    command = PingCommand(client="gt/0.1.0")

    assert command.type == "core.ping"
    assert command.client == "gt/0.1.0"


# 功能：验证 PongResult 会保存 daemon 返回给 CLI 的 ping 结果
# 设计：gt ping 最终要打印 server_version、uptime_ms 和 received_at，所以先固定这三个字段
def test_pong_result_keeps_daemon_status_fields() -> None:
    result = PongResult(
        server_version="0.1.0",
        uptime_ms=12,
        received_at="2026-06-25T00:00:00+00:00",
    )

    assert result.server_version == "0.1.0"
    assert result.uptime_ms == 12
    assert result.received_at == "2026-06-25T00:00:00+00:00"
