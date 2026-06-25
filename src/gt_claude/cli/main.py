import argparse
import asyncio

from gt_claude.cli.commands.ping import run_ping
from gt_claude.cli.commands.version import run_version


# 创建 gt 命令行参数解析器；S0 支持 --version 和 ping
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gt")
    parser.add_argument("--version", action="store_true", help="show GTClaude CLI version")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("ping", help="ping the gt-core daemon")
    return parser


# 异步 CLI 入口；后续 gt ping 会在这里调用异步 socket client
async def async_main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        return run_version()
    if args.command == "ping":
        return await run_ping()

    parser.print_help()
    return 0


# 同步入口；pyproject.toml 里的 gt 命令会调用这个函数
def main() -> None:
    raise SystemExit(asyncio.run(async_main()))
