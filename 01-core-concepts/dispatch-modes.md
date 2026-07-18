# Dispatch Modes — Message Batching Strategy

Dispatch mode controls how OpenAB batches messages before delivering them to the agent. It's a token-cost and coherence trade-off.

## The Three Modes

```toml
[discord]
dispatch_mode = "per-message"   # default
```

### `per-message` (default)

Every message triggers its own ACP turn immediately.

```
User: "what does this function do?"    → ACP turn #1
User: "also why does it use async?"   → ACP turn #2 (separate turn)
```

**Best for:** responsive single-user threads where each message is a complete thought.

**Cost:** each turn carries the full conversation context. Rapid-fire messages = many expensive turns.

### `per-thread`

Consecutive messages in a thread are buffered for a configurable window, then delivered as a single combined message.

```toml
[discord]
dispatch_mode = "per-thread"
dispatch_buffer_ms = 2000   # wait 2 seconds after last message
```

```
User: "what does this function do?"   ─┐
User: "also why does it use async?"   ─┤ buffered
User: "and is it safe to await here?" ─┘
                                        → ACP turn with all 3 combined
```

**Best for:** power users who think-as-they-type, batch-style workflows, or cron-driven messages.

**Cost:** adds latency (buffer window) before agent responds.

### `per-lane`

Each sender in a thread gets their own buffer. Multiple users can be buffered simultaneously.

```toml
[discord]
dispatch_mode = "per-lane"
dispatch_buffer_ms = 1500
```

```
UserA: "help me with X"   → buffered for UserA
UserB: "actually what about Y?" → buffered for UserB (separate lane)
UserA: "specifically X1"  → added to UserA's buffer

After buffer expires:
  UserA lane → ACP turn: "help me with X ... specifically X1"
  UserB lane → ACP turn: "actually what about Y?"
```

**Best for:** shared channels where multiple users collaborate in the same thread without their messages getting entangled.

## Choosing a Mode

```
Is your thread single-user?
  Yes → Is latency critical?
          Yes → per-message
          No  → per-thread (save tokens)
  No  → per-lane
```

See the full decision tree: [Dispatch Mode Picker](../04-decision-trees/dispatch-mode-picker.md)

## Interaction with Cron Jobs

Cron messages are always delivered as their own ACP turn regardless of dispatch mode. They don't get batched with user messages.

## Further Reading

- Source: `crates/openab-core/src/dispatch.rs`
- Docs: `docs/messaging.md`
