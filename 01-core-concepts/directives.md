# Directives — Agent ↔ OpenAB Side-Channel

Directives are structured commands embedded in plain text that let agents and users communicate with OpenAB without the end user seeing the control layer. They're the invisible layer on top of the message.

## Two Kinds

| Kind | Who sends it | When | Stripped before platform? |
|------|-------------|------|--------------------------|
| Output directives | Agent | In agent's response | Yes |
| Control directives | User | In user's first message | Yes |

## Output Directives (Agent → OpenAB)

Agents prefix their response text with `[[key:value]]` blocks. OpenAB strips these before sending to the chat platform.

### `reply_to`

```
[[reply_to:1502606076451885136]]
I agree with point A, but here's why point B is tricky...
```

Tells OpenAB to send this response as a reply to a specific message ID (Discord only currently). Used by agents in multi-bot threads to maintain visual conversation threading.

**Rules:**
- Value max 64 characters
- Alphanumeric + `.`, `-`, `_` only (injection prevention)
- Must appear at the start of the response

### `ephemeral` (planned)

```
[[ephemeral:true]]
Here's the secret context only you can see.
```

Not yet implemented. Will trigger platform-specific ephemeral reply (Discord ephemeral messages, Slack `response_type: ephemeral`).

## Control Directives (User → OpenAB)

Users embed directives in the **first message** of a session (at session creation time). They're immutable once the session starts.

### `[[ws:path]]` — Working Directory

```
@Bot [[ws:~/projects/myapp]] help me debug this crash
```

Sets the agent's working directory for this session.

**Validation rules (strictly enforced):**
- Path must already exist
- Must be within the user's home directory
- No `..` traversal
- Symlinks resolved and checked against home boundary

If validation fails, OpenAB sends an error reply and does not create the session.

### `[[title:text]]` — Thread Title

```
@Bot [[title:Auth refactor — March sprint]] what's wrong with this OAuth flow?
```

Sets the Discord thread title (or equivalent). Useful for organizing long-lived agent threads.

## Why Directives Instead of a Metadata API

The directive design is intentional: it keeps the ACP protocol simple (just text in/text out) while allowing structured coordination. The agent doesn't need to know about platform-specific APIs. It just writes `[[reply_to:ID]]` and OpenAB handles the platform translation.

This also means directives work in any transport that carries text — the ACP pipe, the chat platform, and even log files all capture the same content.

## Parsing Rules

OpenAB's directive parser:
1. Scans the start of the message only (not mid-text)
2. Strips all valid directives before forwarding
3. Leaves malformed or unrecognized directive-like strings intact (no silent failure)
4. Applies a size cap to directive values (prevents DoS via huge directive payloads)

## Further Reading

- Source: `crates/openab-core/src/directives.rs` — parser implementation
- Docs: `docs/output-directives.md` — full output directive reference
- Docs: `docs/control-directives.md` — full control directive reference
- [Multi-Agent](./multi-agent-model.md) — how `reply_to` enables bot-to-bot threading
