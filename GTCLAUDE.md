# GTCLAUDE.md

这个仓库用于分阶段实现 GTClaude：一个本地 mini Claude Code 风格的 Agent Runtime。

## 常用命令

```bash
uv sync
uv run ruff check src tests scripts
uv run mypy src
uv run pytest tests/ -v
uv run python scripts/gen_protocol_doc.py
uv run python scripts/gen_protocol_doc.py --check
uv run gt-core
uv run gt ping
uv run gt --version
```

## S0 架构

S0 只实现 CLI、daemon 和协议骨架：

```text
gt-core
  └─ listens on 127.0.0.1:7437
       ↑ JSON-RPC 2.0 NDJSON
gt CLI
```

协议模型放在 `src/gt_claude/core/bus/`。

`WIRE_PROTOCOL.md` 由 `scripts/gen_protocol_doc.py` 根据协议模型生成，不手写维护。
