# GTClaude

GTClaude 是一个从 0 搭建的本地 Agent Runtime 学习项目。

S0 阶段先建立最小运行边界：

```text
gt CLI
  ↑↓ JSON-RPC 2.0 over NDJSON
gt-core daemon
```

## S0 目标

```bash
uv sync
uv run gt-core
uv run gt ping
```

预期 `gt ping` 输出：

```text
pong server=0.1.0 uptime=...ms latency=...ms
```

## 开发命令

```bash
uv run ruff check src tests scripts
uv run mypy src
uv run pytest tests/ -v
uv run python scripts/gen_protocol_doc.py --check
```
