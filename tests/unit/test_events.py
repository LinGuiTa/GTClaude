from gt_claude.core.bus.events import CoreStartedEvent


# 功能：验证 CoreStartedEvent 会保存 daemon 启动时对外广播的基础信息
# 设计：S0 先只定义一个事件模型，让后续 EventBus 和 TUI 有统一的事件形状可依赖
def test_core_started_event_keeps_daemon_info() -> None:
    event = CoreStartedEvent(
        host="127.0.0.1",
        port=7437,
        server_version="0.1.0",
    )

    assert event.kind == "event"
    assert event.type == "core.started"
    assert event.host == "127.0.0.1"
    assert event.port == 7437
    assert event.server_version == "0.1.0"
