from typing import Literal

from pydantic import BaseModel, Field


class PingCommand(BaseModel):
    # 命令类型；daemon 后续可以根据它识别这是 core.ping 命令
    type: Literal["core.ping"] = "core.ping"

    # 发起 ping 的客户端名称；例如 gt/0.1.0，方便 daemon 知道是谁在探活
    client: str = Field(min_length=1)


class PongResult(BaseModel):
    # daemon 版本；CLI 打印它可以确认自己连到的是哪个版本的 gt-core
    server_version: str

    # daemon 已运行时间，单位毫秒；用于确认 daemon 是刚启动还是已经运行一段时间
    uptime_ms: int

    # daemon 收到 ping 的时间；用于 trace/debug 时对齐客户端和服务端时间线
    received_at: str
