# GTClaude 技术方案

## 项目定位

GTClaude 是一个从 0 实现的本地 Agent Runtime，目标不是做聊天机器人，而是做一个可演进的 mini Claude Code。

核心链路：

```text
用户目标
  → gt CLI
  → gt-core daemon
  → AgentRunner
  → AgentLoop
  → LLM Provider
  → ToolRegistry
  → PermissionManager
  → EventBus
  → Session / Trace / Memory
```

第一阶段重点是理解和实现 Agent 的工程骨架：CLI、daemon、协议、事件、工具、权限和上下文。长期目标是支持本地 coding agent、工具调用、权限审批、事件流展示、session 续航、context compact、skills、subagents、MCP 和 TUI。

## 总体架构

GTClaude 采用双进程架构：

```text
gt CLI / gt-tui
     ↑↓ JSON-RPC 2.0 over NDJSON
gt-core daemon
     ↓
Agent runtime
```

CLI/TUI 是客户端，`gt-core` 是真正执行任务的 Agent runtime。这个边界从 S0 开始建立，避免后续加入 TUI、多客户端、事件订阅和权限审批时推倒重来。

双进程架构的收益：

- 后续可以同时接 CLI、TUI、Web。
- Agent run 不依赖某个终端窗口生命周期。
- 事件流可以被多个客户端订阅。
- 权限审批可以通过事件推到前端。
- trace、session、上下文都集中在 core 管理。
- 适合讲系统设计、协议建模和 Agent runtime。

## 模块划分

建议项目结构：

```text
GTClaude/
├── pyproject.toml
├── README.md
├── GTCLAUDE.md
├── WIRE_PROTOCOL.md
├── src/
│   └── gt_claude/
│       ├── cli/
│       │   ├── main.py
│       │   └── commands/
│       │       ├── ping.py
│       │       ├── run.py
│       │       └── version.py
│       ├── core/
│       │   ├── app.py
│       │   ├── config.py
│       │   ├── bus/
│       │   │   ├── envelope.py
│       │   │   ├── commands.py
│       │   │   └── events.py
│       │   ├── transport/
│       │   │   ├── socket_server.py
│       │   │   └── socket_client.py
│       │   ├── llm/
│       │   │   ├── base.py
│       │   │   └── provider.py
│       │   ├── tools/
│       │   │   ├── base.py
│       │   │   ├── registry.py
│       │   │   └── invocation.py
│       │   ├── permissions/
│       │   │   ├── policy.py
│       │   │   └── manager.py
│       │   ├── events/
│       │   │   ├── bus.py
│       │   │   └── writer.py
│       │   ├── session/
│       │   │   ├── model.py
│       │   │   └── store.py
│       │   ├── trace/
│       │   │   └── writer.py
│       │   ├── context.py
│       │   ├── loop.py
│       │   └── runner.py
│       └── tui/
│           └── app.py
└── tests/
    ├── unit/
    └── integration/
```

第一阶段只实现 S0 需要的核心骨架，不一次性填满所有模块。

## 通信协议

GTClaude 使用 JSON-RPC 2.0 over NDJSON。每条消息是一行 JSON：

```json
{"jsonrpc":"2.0","id":"u-1","method":"core.ping","params":{"client":"gt/0.1.0"}}
```

响应：

```json
{"jsonrpc":"2.0","id":"u-1","result":{"server_version":"0.1.0","uptime_ms":12}}
```

选择 NDJSON 的原因：

- 简单。
- 可流式。
- 适合事件订阅。
- 终端调试方便。
- 后续 TUI/Web 都能复用。

所有命令和事件都用 Pydantic 定义。协议模型包括：

```text
Command
  - PingCommand
  - AgentRunCommand
  - SubscribeRunCommand
  - PermissionReplyCommand

Event
  - CoreStartedEvent
  - RunStartedEvent
  - LlmTokenEvent
  - ToolCallStartedEvent
  - ToolCallFinishedEvent
  - PermissionRequestedEvent
  - RunFinishedEvent
```

`WIRE_PROTOCOL.md` 由模型自动生成，避免文档和代码漂移。

## Agent Loop 设计

核心 loop：

```text
while not done:
    1. 构造 messages/context
    2. 调用 LLM
    3. 如果 LLM 输出 final answer → 结束
    4. 如果 LLM 请求 tool_use
       - 校验 tool 参数
       - 检查权限
       - 执行 tool
       - 将 tool_result 写回 messages
    5. 发出事件
```

第一版只实现最小闭环：

```text
用户 goal
  → LLM
  → final answer
```

第二版加入工具：

```text
用户 goal
  → LLM tool_use
  → read_file / list_dir
  → tool_result
  → LLM final answer
```

## Tool 系统设计

工具不直接裸函数暴露给模型，而是统一注册到 `ToolRegistry`：

```text
ToolRegistry
  ├── read_file
  ├── list_dir
  ├── write_file
  ├── run_shell
  └── spawn_agent
```

每个工具包含：

```text
name
description
input_schema
risk_level
handler
```

工具风险等级：

```text
readonly         可直接执行
workspace_write  需要确认
shell            默认需要确认
external_write   必须确认
dangerous        默认禁止
```

第一阶段只做只读工具：`read_file` 和 `list_dir`。

## 权限系统设计

权限系统不靠 prompt，而由 runtime 强制。

流程：

```text
LLM 请求 tool_use
  → ToolRegistry 找到工具
  → PermissionManager 判断风险
  → 如果需要确认，发 PermissionRequestedEvent
  → CLI/TUI 展示审批
  → 用户 allow/deny
  → runtime 执行或返回拒绝结果
```

第一阶段只预留模型和事件，不实现复杂 UI。

## EventBus 设计

所有关键过程都转成事件：

```text
RunStarted
LlmRequestStarted
LlmToken
LlmRequestFinished
ToolCallStarted
ToolCallFinished
PermissionRequested
RunFinished
RunFailed
```

事件用途：

1. 给 CLI/TUI 实时展示。
2. 写入 `events.jsonl` 供复盘。

## Session / Trace / Memory 设计

### Session

Session 表示多轮上下文：

```text
session_id
thread_id
messages
notes
created_at
updated_at
```

### Trace

Trace 表示一次 run 的系统级轨迹：

```text
run_id
events.jsonl
tool_calls
model_requests
permission_decisions
errors
```

### Memory

长期记忆后面再加，第一阶段只设计接口：

```text
MemoryStore
  - load_project_notes()
  - save_note()
  - search_notes()
```

## 阶段落地路线

### S0：项目骨架与协议契约

目标：

```text
gt-core daemon 能启动
gt CLI 能 ping daemon
JSON-RPC/NDJSON 通信跑通
WIRE_PROTOCOL.md 可生成
```

验收：

```bash
uv run gt-core
uv run gt ping
# 输出 pong server=0.1.0 latency=xxms
```

产物：

```text
pyproject.toml
src/gt_claude/core/bus/*
src/gt_claude/core/transport/*
src/gt_claude/core/app.py
src/gt_claude/cli/*
tests/unit/test_envelope.py
tests/integration/test_ping_roundtrip.py
WIRE_PROTOCOL.md
```

### S1：最小 Agent Run

目标：

```text
gt run "一句目标"
→ daemon 创建 run
→ 调 LLM
→ 返回最终回答
→ 写 events.jsonl
```

验收：

```bash
uv run gt run "用一句话解释什么是 Agent Loop"
```

产物：

```text
LLM Provider
AgentRunner
RunStarted / RunFinished events
events writer
```

### S2：事件流外化

目标：

```text
CLI 不再只等最终结果，而是订阅 run event stream
```

验收：

```text
运行 gt run 时能看到：
- run started
- llm request started
- token streaming
- run finished
```

产物：

```text
EventBus
SubscribeRunCommand
IPC broadcaster
```

### S3：Tool Use 最小闭环

目标：

```text
LLM 可以调用 read_file / list_dir
tool_result 回填给模型
```

验收：

```bash
uv run gt run "总结 README.md 的内容"
```

产物：

```text
Tool base
ToolRegistry
ToolInvocation
read_file
list_dir
tool_use parsing
```

### S4：权限审批

目标：

```text
写文件 / shell 命令需要用户确认
```

验收：

```text
Agent 想写文件时：
CLI/TUI 显示审批
用户 allow 才执行
deny 则返回拒绝结果
```

产物：

```text
PermissionManager
PermissionRequestedEvent
PermissionReplyCommand
policy storage
```

### S5：Session 与记忆

目标：

```text
多轮 run 共享 session
notes 保存关键上下文
```

验收：

```bash
gt chat
# 第一轮告诉它项目背景
# 第二轮能基于 session 延续
```

产物：

```text
SessionStore
Thread
Notes
chat command
```

### S6：Context 治理与 Compact

目标：

```text
上下文过长时检测水位
截断 tool_result
触发 compact
```

验收：

```text
长会话下不会无限堆 messages
events 中能看到 context budget / compact 事件
```

产物：

```text
ContextBuilder
TokenBudget
Compactor
CompactEvent
```

### S7：Skills / Subagents / MCP

目标：

```text
支持从 skills/ 加载任务 playbook
支持 spawn subagent
支持 MCP 工具接入
```

验收：

```bash
gt run "/code-review 检查这个 diff"
```

产物：

```text
SkillLoader
SubagentRegistry
MCPClient
MCPToolAdapter
```

## 第一阶段范围

当前只实现 S0：CLI + daemon + JSON-RPC/NDJSON + ping。

S0 完成后可以说明：

```text
我没有直接写一个单进程脚本，而是先建立了本地 Agent runtime 的客户端/核心进程边界；CLI 通过类型化 JSON-RPC over NDJSON 调用 daemon；协议文档由 Pydantic 模型生成，确保 wire protocol 与代码同源。
```

## 技术栈

```text
语言：Python 3.12
依赖管理：uv
协议建模：pydantic v2
测试：pytest + pytest-asyncio
类型检查：mypy strict
Lint：ruff
TUI：textual（S2/S3 后再加）
LLM SDK：Anthropic 或兼容 Provider abstraction
```

选择 Python 的原因：

- 生态成熟。
- Agent 工具写起来快。
- Pydantic 适合协议建模。
- Textual 适合 TUI。
- pytest/mypy/ruff 可展示工程质量。

## 设计原则

1. **先 runtime，后智能**：不急着让模型很聪明，先把运行链路做稳。
2. **协议先行**：CLI/TUI 和 core 之间只通过 typed protocol 通信。
3. **事件优先**：Agent 过程不能是黑盒，所有关键步骤都事件化。
4. **工具必须有边界**：Tool 不裸跑，必须经过 schema 校验和权限管理。
5. **每阶段可验收**：每个阶段都有命令可跑、有测试可过、有文档可讲。
