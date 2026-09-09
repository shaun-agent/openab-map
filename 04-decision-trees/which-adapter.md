# Which Adapter? Native vs Gateway

> **Not a chat platform at all?** To drive an agent from an IDE, browser, or CLI, use the ACP server endpoint at `/acp`. It requires v0.10.0-beta.2+ and `OPENAB_ACP_ENABLED=true`; see [Drive Your Agent from an ACP Client](../03-use-cases/drive-agent-from-acp-client.md).

```mermaid
flowchart TD
    PLAT[Which platform?] --> DC{Discord?}
    PLAT --> SL{Slack?}
    PLAT --> OTHERS{Telegram / LINE / LINE WORKS\nFeishu / Teams\nGoogle Chat / WeCom?}

    DC --> DC_YES[Native adapter\nbuilt into openab binary\nno gateway needed]
    SL --> SL_YES[Native adapter\nbuilt into openab binary\nno gateway needed]

    OTHERS --> DEPLOY{Deployment model?}
    DEPLOY -->|Simplest ops| UNIFIED[Unified build\ngateway compiled in\nsame binary]
    DEPLOY -->|Need to scale gateway independently| SPLIT[Separate gateway pod\nopenab-gateway binary]
    DEPLOY -->|Multiple webhook platforms| SPLIT
```

## Why Two Tiers Exist

**Native adapters (Discord, Slack)** use persistent outbound WebSocket connections. OpenAB connects out to the platform — no inbound firewall rules needed, no TLS cert management for webhooks.

**Gateway-based adapters** work with webhook-based platforms. The platform sends HTTP POST events to your endpoint. The gateway receives them, normalizes them, and forwards to the main broker via an internal WebSocket.

## When to Use the Gateway

You need the gateway when running any of:
- Telegram
- LINE
- LINE WORKS *(v0.10.0-beta.3+)*
- Feishu / Lark
- Google Chat
- WeCom
- Microsoft Teams

**Google Chat** *(v0.10.0-beta.4+)*: keyless ADC auth via `GOOGLE_CHAT_USE_ADC` requires `GOOGLE_CHAT_ADC_TARGET_SERVICE_ACCOUNT` (config `adc_target_service_account`), a dedicated Chat-app service account distinct from the attached runtime SA. The runtime SA impersonates that target through IAM Credentials `generateAccessToken`; Google prohibits self-impersonation (`FAILED_PRECONDITION`), and `use_adc=true` without a target fails closed. A successfully loaded SA key wins; an unloadable configured key falls back to ADC with a logged identity switch; static token is last resort. Replies are send-once, without streaming edits, because the platform limits writes to 1/second/space.

## Unified Build vs Separate Gateway Pod

**Unified build** (default for simple deployments):
```dockerfile
# Dockerfile.unified — all adapters compiled in
FROM rust:1-bookworm AS builder
RUN cargo build --features unified
```

One binary, one pod, handles everything. Simplest ops. The `unified` feature bundle includes `acp`. Use this unless you have a reason not to.

**Separate gateway pod:**
```yaml
# Two deployments in Helm
agents:
  main:
    # openab binary — Discord/Slack native
gateway:
  enabled: true
  platforms: [telegram, line, feishu]
```

Use separate pods when:
- Gateway receives high webhook traffic (scale it independently)
- You want network isolation (gateway in DMZ, broker in private subnet)
- Gateway and broker need different resource profiles
- You're running Discord/Slack natively and adding a webhook platform later

## Platform Capability Differences

| Platform | Threads | Reactions | Slash cmds | Voice→Text | Edit msgs |
|----------|---------|-----------|-----------|-----------|----------|
| Discord | ✓ | ✓ | ✓ | ✓ | ✓ |
| Slack | ✓ | ✓ | — | — | ✓ |
| Telegram | simulated | — | — | ✓ | — |
| LINE | simulated | — | — | — | — |
| LINE WORKS *(v0.10.0-beta.3+)* | — | — | — | ✓ | — |
| Feishu | ✓ | ✓ | — | — | ✓ |
| Teams | ✓ | limited | — | — | ✓ |

If you need slash commands or reaction-based status indicators, Discord is the richest platform.

## Adding a New Platform

Implement `ChatAdapter` in `crates/openab-gateway/src/`. The gateway pattern is the recommended extension point. See `crates/openab-gateway/src/telegram.rs` as a reference implementation.
