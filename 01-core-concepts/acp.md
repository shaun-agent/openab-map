# ACP — Agent Client Protocol

ACP is the contract between OpenAB and agents. If you understand ACP, you understand how any agent plugs in.

## What It Is

ACP is **JSON-RPC 2.0 over stdio pipes**. Not HTTP. Not WebSockets. Just stdin/stdout.

OpenAB spawns your agent as a subprocess and speaks to it by writing JSON to its stdin. The agent writes JSON to stdout. OpenAB reads it. That's the entire transport.

```
OpenAB process
    │
    ├── stdin  ──→  agent subprocess
    └── stdout ←──  agent subprocess
```

This means any CLI that can read from stdin and write to stdout can be an ACP agent. No network ports. No authentication to OpenAB. No SDK required.

## Message Flow

```mermaid
sequenceDiagram
    participant OAB as OpenAB
    participant A as Agent CLI

    OAB->>A: initialize (capabilities handshake)
    A-->>OAB: initialized (accepted capabilities)

    OAB->>A: session/new {session_id, config}
    A-->>OAB: session/new result

    OAB->>A: session/send_message {content, sender}
    Note over A: Agent processes, may call tools
    A-->>OAB: tool/call_request (ask permission)
    OAB-->>A: tool/call_response (auto-approved or denied)
    A-->>OAB: content_block (streaming text)
    A-->>OAB: content_block (thinking block if enabled)
    A-->>OAB: session/send_message result (turn complete)

    OAB->>A: session/cancel (if user cancels)
```

## Key Message Types

| Method | Direction | Purpose |
|--------|-----------|---------|
| `initialize` | OAB → Agent | Capability negotiation (tool auto-reply, thinking, edit-streaming) |
| `session/new` | OAB → Agent | Create a new conversation session |
| `session/send_message` | OAB → Agent | Deliver a user message, start a turn |
| `session/cancel` | OAB → Agent | Abort an in-flight turn |
| `session/set_config_option` | OAB → Agent | Change runtime config (model, etc.) |
| `content_block` | Agent → OAB | Streaming text chunk |
| `tool/call_request` | Agent → OAB | Agent wants to run a tool |
| `tool/call_response` | OAB → Agent | OpenAB approves/denies tool call |

## What Agents Don't Know

The agent sees:
- A user message with sender metadata
- Tool call results (auto-replied by OpenAB)
- Session config

The agent does NOT see:
- Which platform the message came from
- OpenAB's config
- Other sessions

This isolation is intentional. Agents stay platform-agnostic.

## Making a CLI ACP-Compatible

The agent needs a subcommand that starts an ACP stdio server:

```bash
kiro-cli acp                    # Kiro
claude-agent-acp                # Claude Code adapter
codex-acp                       # Codex adapter
gemini --acp                    # Gemini
opencode acp                    # OpenCode
openab-agent                    # Native openab agent
```

Then in `config.toml`:

```toml
[agent]
command = "kiro-cli"
args = ["acp", "--trust-all-tools"]
```

That's it. OpenAB spawns the subprocess and speaks ACP to it.

## Tool Call Auto-Reply

By default, OpenAB auto-approves all tool calls from the agent. This is what `--trust-all-tools` signals. If an agent requests a sensitive tool call without this flag, OpenAB can be configured to prompt a human (via a slash command) before replying.

## Thinking Blocks

If the agent emits a `thinking` content block (chain-of-thought), OpenAB passes it through to the session but strips it before sending the final message to the chat platform. Users don't see thinking blocks.

## Further Reading

- Source: `crates/openab-core/src/acp/` — protocol types and session lifecycle
- [Sessions](./sessions.md) — how ACP sessions map to conversation threads
- [Which Agent?](../04-decision-trees/which-agent.md) — choosing an agent CLI
