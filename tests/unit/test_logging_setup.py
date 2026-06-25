import logging

from gt_claude.core.logging_setup import setup_logging


# 功能：验证 setup_logging 会把 root logger 设置成传入的日志级别
# 设计：daemon 启动时只需要先能控制日志级别，所以这里先不测试日志输出格式
def test_setup_logging_sets_root_logger_level() -> None:
    setup_logging("DEBUG")

    assert logging.getLogger().level == logging.DEBUG
