import pytest

from gt_claude.core.config import CoreConfig, load_config


# 功能：验证没有任何环境变量时，core 使用固定默认配置
# 设计：传入空字典而不是读取真实 os.environ，保证测试不受本机环境影响
def test_load_config_uses_defaults_when_env_is_empty() -> None:
    config = load_config(env={})

    assert config == CoreConfig(
        host="127.0.0.1",
        port=7437,
        log_level="INFO",
    )


# 功能：验证环境变量可以覆盖 host、port 和 log_level
# 设计：用显式 env 字典模拟 shell 环境，避免修改真实环境变量造成测试污染
def test_load_config_reads_overrides_from_env() -> None:
    config = load_config(
        env={
            "GT_HOST": "127.0.0.2",
            "GT_PORT": "8000",
            "GT_LOG_LEVEL": "DEBUG",
        }
    )

    assert config.host == "127.0.0.2"
    assert config.port == 8000
    assert config.log_level == "DEBUG"


# 功能：验证 GT_PORT 必须是整数
# 设计：端口不合法应该在配置层尽早失败，不要等到 socket server 启动时才报错
def test_load_config_rejects_invalid_port() -> None:
    with pytest.raises(ValueError, match="GT_PORT must be an integer"):
        load_config(env={"GT_PORT": "not-a-number"})
