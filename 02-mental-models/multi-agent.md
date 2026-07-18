# Multi-Agent — How Bots Collaborate

OpenAB is designed for multi-bot channels from day one. Each bot is a fully independent pod. Coordination happens through the platform itself.

## The Mental Model

There is no shared bus, no inter-pod communication channel, no orchestrator. Bots collaborate exactly as humans do — by reading and responding to messages in the channel.

```mermaid
graph TB
    subgraph Discord["Discord Channel: engineering"]
        MSG1["UserA: @Kiro help me plan this feature"]
        MSG2["Kiro: Here is a plan: step 1, 2, 3"]
        MSG3["UserA: @Claude review Kiro's plan"]
        MSG4["Claude: Point 2 has a flaw\nreply_to MSG2\nHere is why..."]
    end

    subgraph Infra["Infrastructure"]
        K["openab-kiro Pod\nSession Pool"]
        C["openab-claude Pod\nSession Pool"]
    end

    MSG1 --> K
    K --> MSG2
    MSG3 --> C
    C --> MSG4
```

KiroBot and ClaudeBot don't know each other exists at the infrastructure level. They see the same Discord channel. The `[[reply_to:ID]]` directive creates visual threading in Discord so it's clear which bot is responding to which message.

## Bot-to-Bot Turn Flow

```mermaid
sequenceDiagram
    actor User
    participant DC as Discord
    participant K as openab-kiro
    participant C as openab-claude

    User->>DC: "@Kiro plan feature X"
    DC->>K: MESSAGE_CREATE (mention)
    K->>DC: "Here's my plan..."

    Note over DC: Claude sees this message too
    DC->>C: MESSAGE_CREATE (bot message)
    C->>C: allow_bot_messages = "mentions"?
    C->>C: No @mention → ignore

    User->>DC: "@Claude critique Kiro's plan"
    DC->>C: MESSAGE_CREATE (mention)
    C->>DC: reply_to KIRO_MSG_ID — Point 2 has a flaw...

    Note over DC: Kiro sees this reply too
    DC->>K: MESSAGE_CREATE (bot message, no @mention)
    K->>K: allow_bot_messages = "mentions"?
    K->>K: No @mention → ignore
```

## Bot Loop Prevention

Without safeguards, two bots with `allow_bot_messages = "all"` will talk to each other forever. OpenAB prevents this:

```toml
[discord]
max_bot_turns = 100      # consecutive bot→bot turns before hard stop
```

When the counter hits `max_bot_turns`, OpenAB stops delivering bot messages to the session until a human sends a message (which resets the counter).

The compiled-in ceiling is 1000 — no config value overrides this.

## Trusted Bot Patterns

For intentional b2b pipelines (e.g., Kiro drafts, Claude reviews, Claude's output goes back to Kiro):

```toml
# openab-kiro config
[discord]
allow_bot_messages = "mentions"
trusted_bot_ids = ["CLAUDE_BOT_ID"]   # only Claude's messages are eligible
max_bot_turns = 10                     # tight cap for review loops
```

```toml
# openab-claude config
[discord]
allow_bot_messages = "off"   # Claude only responds to humans
```

This creates a one-way pipe: human → Kiro → Claude (reviews) → done. Claude doesn't pick up Kiro's response to its review.

## Multi-Agent Review Pattern (openab-map use case)

The workflow that keeps this repo updated uses a multi-agent review:

```mermaid
sequenceDiagram
    participant GH as GitHub Action
    participant OAB_D as openab-draftor
    participant DC as Discord
    participant OAB_R1 as openab-reviewer-1
    participant OAB_R2 as openab-reviewer-2
    participant GH2 as GitHub (auto-merge)

    GH->>DC: "New diff ready. Draft PR."
    DC->>OAB_D: session/send_message
    OAB_D->>GH: Opens PR with map updates
    OAB_D->>DC: "PR #42 opened. Requesting review."

    DC->>OAB_R1: (mention) Review PR #42
    DC->>OAB_R2: (mention) Review PR #42
    OAB_R1->>DC: "LGTM — data flow section is accurate."
    OAB_R2->>DC: "One issue: session TTL default is wrong."

    OAB_D->>DC: (sees R2's comment) Fixing...
    OAB_D->>GH: Pushes fix to PR #42
    OAB_D->>DC: "Fixed. Re-requesting review."

    OAB_R1->>DC: "LGTM"
    OAB_R2->>DC: "LGTM"
    GH2->>GH: Auto-merge (2/2 approved)
```

This entire flow is OpenAB doing what it does — routing messages between humans, bots, and GitHub — with no special orchestration layer.

## Further Reading

- Docs: `docs/multi-agent.md`
- [Trust Model](../01-core-concepts/trust-model.md) — `trusted_bot_ids`, `max_bot_turns`
- [Dispatch Modes](../01-core-concepts/dispatch-modes.md) — `per-lane` for multi-user threads
