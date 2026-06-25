import pytest

from gt_claude.cli.main import async_main


# 功能：验证 gt --version 会打印当前 CLI 版本并返回成功状态码
# 设计：直接调用 async_main，避免启动子进程，让这个测试只关注 CLI 参数路由本身
@pytest.mark.asyncio
async def test_cli_version_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = await async_main(["--version"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "gt 0.1.0\n"
