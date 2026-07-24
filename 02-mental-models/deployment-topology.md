# Deployment Topology

How OpenAB actually runs in production: what pods exist, what talks to what, and where things live.

## Minimal: Single Agent, Discord

```mermaid
graph TB
    subgraph "Internet"
        DC[Discord Gateway<br/>WebSocket]
        ANTHROPIC[Anthropic API]
    end

    subgraph "Kubernetes Cluster"
        subgraph "openab Pod"
            OAB[openab binary<br/>adapter: Discord]
            subgraph "Session Pool"
                S1[kiro-cli acp<br/>PID 8821<br/>session: thread-42]
                S2[kiro-cli acp<br/>PID 8822<br/>session: thread-99]
            end
            PVC[PVC<br/>~/ workdir]
        end
        SECRET[K8s Secret<br/>DISCORD_BOT_TOKEN<br/>ANTHROPIC_API_KEY]
    end

    DC <-->|WebSocket| OAB
    OAB <-->|ACP stdio| S1
    OAB <-->|ACP stdio| S2
    S1 <-->|HTTPS| ANTHROPIC
    S2 <-->|HTTPS| ANTHROPIC
    OAB -.->|envFrom| SECRET
    S1 --- PVC
    S2 --- PVC
```

One pod. One ACP subprocess per active thread. PVC for working directory persistence.

## Multi-Agent: Two Bots, One Channel

```mermaid
graph TB
    subgraph "Internet"
        DC[Discord Gateway]
    end

    subgraph "Kubernetes Cluster"
        subgraph "openab-kiro Pod"
            OAB1[openab binary<br/>bot: KiroBot<br/>token: BOT_TOKEN_1]
            K1[kiro-cli acp sessions]
        end

        subgraph "openab-claude Pod"
            OAB2[openab binary<br/>bot: ClaudeBot<br/>token: BOT_TOKEN_2]
            C1[claude-agent-acp sessions]
        end
    end

    DC <-->|WebSocket| OAB1
    DC <-->|WebSocket| OAB2

    OAB1 -.->|b2b via Discord| OAB2
```

Each bot is an independent pod with its own token, session pool, and ACP subprocess fleet. They coordinate via the platform itself (Discord messages) — not via any shared internal channel.

## With Gateway (Webhook Platforms)

```mermaid
graph TB
    subgraph "Internet"
        DC[Discord]
        TG[Telegram]
        MS[Microsoft Teams]
    end

    subgraph "Kubernetes Cluster"
        subgraph "openab Pod"
            OAB[openab binary<br/>Discord adapter]
        end

        subgraph "openab-gateway Pod"
            GW[openab-gateway binary<br/>Telegram + Teams adapters]
        end

        SESSIONS[Shared agent session pool]
    end

    DC <-->|WebSocket| OAB
    TG -->|Webhook POST| GW
    MS -->|Webhook POST| GW
    GW <-->|Internal WebSocket| OAB
    OAB <--> SESSIONS
```

The gateway normalizes webhook events and forwards them to the main broker as if they came from a native adapter. From the session pool's perspective, all platforms look the same.

## AWS ECS Fargate

```mermaid
graph TB
    subgraph "AWS"
        subgraph "ECS Service"
            TASK[ECS Task<br/>openab container<br/>agent container]
        end
        SM[Secrets Manager<br/>bot tokens, API keys]
        S3[S3 Bucket<br/>pre-seed archives<br/>workspace backups]
        ECR[ECR<br/>container images]
    end

    TASK -.->|aws-sm:// resolution| SM
    TASK -.->|pre_seed / pre_shutdown| S3
    ECR -.->|image pull| TASK
```

On ECS, secrets come from Secrets Manager via the `aws-sm://` syntax. Workspace persistence uses S3 (pre_seed hook downloads, pre_shutdown hook uploads).

## AWS AgentCore

AgentCore runs each agent session in its own **microVM** (Firecracker-based), providing hardware-level isolation. OpenAB runs as the broker outside the microVMs; the ACP interface is unchanged.

```mermaid
graph LR
    OAB[OpenAB Broker] <-->|ACP stdio| AC[AgentCore Runtime]
    subgraph "AgentCore Runtime"
        VM1[microVM: session-42<br/>kiro-cli]
        VM2[microVM: session-99<br/>kiro-cli]
    end
    AC --- VM1
    AC --- VM2
```

## ACP Client Endpoint (v0.10.0-beta.2+)

```mermaid
flowchart LR
    C[Zed / Browser] -->|WS(S) /acp| O[openab Pod]
    K["Non-loopback: bearer key required<br/>Localhost: keyless allowed"] -.-> O
```

Standard ACP clients can drive the pod directly through its WebSocket endpoint. Set `OPENAB_ACP_AUTH_KEY` on non-loopback binds; keyless access is allowed only on localhost.

## Local Development

```bash
openab run -c config.toml
```

Runs entirely on localhost. No containers, no K8s. Not suitable for production (no sandboxing).

## Further Reading

- Helm chart: `charts/openab/values.yaml`
- ECS: `operator/` — oabctl CLI for ECS control plane
- [Hooks](../01-core-concepts/hooks.md) — pre_seed / pre_shutdown for S3 persistence
