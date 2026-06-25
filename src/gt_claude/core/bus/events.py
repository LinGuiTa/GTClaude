from typing import Literal

from pydantic import BaseModel


class CoreStartedEvent(BaseModel):
    # 事件信封标记；后续客户端可以用 kind 区分“响应消息”和“事件消息”
    kind: Literal["event"] = "event"

    # 事件类型；core.started 表示 gt-core daemon 已启动
    type: Literal["core.started"] = "core.started"

    # daemon 监听地址；客户端和日志都可以看到 core 实际绑定在哪里
    host: str

    # daemon 监听端口；S0 默认是 7437，测试中也可以用随机端口
    port: int

    # daemon 版本；用于排查 CLI 和 core 版本是否一致
    server_version: str
