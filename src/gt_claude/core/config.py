import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class CoreConfig:
    # gt-core 监听地址；默认只监听本机，避免暴露到局域网或公网
    host: str = "127.0.0.1"

    # gt-core 监听端口；7437 是 GTClaude S0 的固定默认端口
    port: int = 7437

    # 日志级别；后续 logging_setup 会用它配置 daemon 日志
    log_level: str = "INFO"


# 从环境变量加载 core 配置；测试时可以传 env 字典隔离真实系统环境
def load_config(env: Mapping[str, str] | None = None) -> CoreConfig:
    source = os.environ if env is None else env
    raw_port = source.get("GT_PORT", "7437")

    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError("GT_PORT must be an integer") from exc

    return CoreConfig(
        host=source.get("GT_HOST", "127.0.0.1"),
        port=port,
        log_level=source.get("GT_LOG_LEVEL", "INFO"),
    )
