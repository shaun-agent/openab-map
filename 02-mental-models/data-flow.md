# Data Flow — Message End to End

The full journey of a message, from a user typing in Discord to the agent's response appearing in the thread.

## Happy Path

```mermaid
sequenceDiagram
    actor User
    participant Discord
    participant OAB as OpenAB Broker
    participant Pool as Session Pool
    participant Agent as Agent CLI (kiro-cli acp)

    User->>Discord: "@Bot help me debug this crash"
    Discord-->>OAB: MESSAGE_CREATE event (WebSocket)

    OAB->>OAB: Check: allowed channel? ✓
    OAB->>OAB: Check: @mention required? ✓
    OAB->>OAB: Parse control directives (none)
    OAB->>Discord: Add 👀 reaction

    OAB->>Pool: route(thread_id="42")
    Pool->>Pool: No session for thread 42
    Pool->>Agent: spawn subprocess
    Agent-->>Pool: ACP initialize handshake
    Pool->>Agent: session/new {session_id, config}
    Agent-->>Pool: session created

    Pool->>Agent: session/send_message {content, sender}
    OAB->>Discord: Update reaction 🤔

    loop Agent processing
        Agent->>Agent: LLM inference
        Agent-->>Pool: content_block (streaming text)
        OAB->>Discord: Stream response to thread
        OAB->>Discord: Update reaction 🔥
    end

    Agent-->>Pool: turn complete
    OAB->>Discord: Final message posted
    OAB->>Discord: Remove reactions + add 👍
```

## What Gets Stripped

Before the response reaches Discord, OpenAB strips:

1. **Output directives** — `[[reply_to:ID]]`, etc. (never shown to user)
2. **Thinking blocks** — chain-of-thought content from agent's reasoning
3. **Tool call details** — agent tool requests/responses (internal)

What the user sees is only the text content the agent intended for them.

## Media Processing

If the message contains attachments (images, files, audio):

```mermaid
flowchart LR
    MSG[Message + attachment] --> MT{Type?}
    MT -->|image| DL[Download]
    MT -->|audio| STT[Speech-to-text<br/>Groq Whisper / OpenAI]
    MT -->|file| DL
    DL --> EMBED[Embed in message content]
    STT --> EMBED
    EMBED --> AGENT[→ Agent]
```

Audio messages (Discord voice messages, Telegram voice notes) are transcribed before the agent sees them. The agent receives text — it never sees raw audio.

## Concurrent Thread Handling

OpenAB handles multiple threads concurrently without queuing:

```mermaid
flowchart TD
    subgraph "Incoming"
        M1[Thread 42: message]
        M2[Thread 99: message]
        M3[Thread 42: another message]
    end

    subgraph "Session Pool"
        S42[Session 42<br/>kiro PID 8821]
        S99[Session 99<br/>kiro PID 9012]
    end

    M1 --> S42
    M2 --> S99
    M3 -->|queued until turn complete| S42
```

Within a single thread, messages are serialized — the second message waits for the first turn to complete. Across threads, everything is concurrent (up to the pool's max sessions).

## Error Paths

| Error | What happens |
|-------|-------------|
| Agent subprocess crashes | Session evicted, error message sent to thread |
| Platform WebSocket drops | Adapter reconnects with backoff |
| ACP turn timeout | Session cancelled, error message sent |
| Pool full + all sessions active | Message queued (configurable timeout, then dropped) |
| Secret resolution fails at boot | Process exits — never starts in broken state |
