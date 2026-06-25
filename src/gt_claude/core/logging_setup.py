import logging


# 配置 gt-core 的基础日志级别；level 来自 CoreConfig.log_level，例如 INFO 或 DEBUG
def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
