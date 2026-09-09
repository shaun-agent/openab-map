# Agent Control Plane — Direct Agent-to-Agent Delegation

> **Status:** ADR accepted; PR 1/4 shipped the standalone `openab-cp` binary—registry, router, and policy; PR 2/4 shipped its observer/lobby read surface. Runtime integration, agent-facing tools, CLI, and client relay streaming remain pending. **Unreleased — on `main` after v0.10.0-beta.4.**

The symmetry is simple: **the gateway routes human↔agent messages; the control plane routes agent↔agent messages.**

The Agent Control Plane is a standalone hub-and-spoke service for direct delegation between OpenAB runtimes. It uses a private WebSocket protocol instead of sending orchestration traffic through a chat platform.

## Why a Separate Path

Chat-based bot-to-bot remains the right mechanism when humans should see and participate in the collaboration. It is a poor transport for machine delegation:

| Chat-platform b2b pain | Control-plane answer |
|------------------------|----------------------|
| Discord rate limits around 5 messages/second | Structured direct routing over WebSocket |
| Per-hop platform latency | Low-latency runtime-to-runtime path |
| 2,000-character formatting constraints | Prompts and results up to configured byte caps |
| Orchestration noise in human channels | Private delegation traffic |

The control plane complements chat collaboration; it does not replace it.

## Architecture

```mermaid
flowchart LR
    A[Agent A]
    OA[OAB-A]
    CP["openab-cp<br/>registry + router + policy"]
    OB[OAB-B]
    B[Agent B]

    A -->|planned spawn_agent tool| OA
    OA -->|cp/delegate| CP
    CP -->|route to live worker| OB
    OB --> B
    B --> OB -->|cp/delegate_result| CP --> OA --> A
```

## Three Responsibilities

| Part | Responsibility |
|------|----------------|
| **Registry** | Runtimes register outbound with namespace, name, type (`primary`, `worker`, or `observer`), labels, and `max_delegated_sessions`. Heartbeats run every 15 seconds; leases expire after 45 seconds. |
| **Router** | Resolves a target by name or labels to a live, non-saturated instance, forwards the delegation, and routes the result back. |
| **Policy** | Enforces namespace policy centrally. By default only primaries may initiate, maximum depth is 1, worker→worker is denied, cycles are rejected, and cross-namespace delegation is denied. |

Registry state is intentionally ephemeral. A control-plane restart rebuilds it as runtimes reconnect and re-register.

## Wire Contract

Frames are JSON-RPC-style messages over WebSocket:

| Method | Purpose |
|--------|---------|
| `cp/register` | Must be the first frame; registers the runtime identity and capacity, and returns heartbeat/lease timing. |
| `cp/heartbeat` | Keeps the registration alive at the returned interval; missing heartbeats beyond `lease_expiry_secs` deregister the runtime. |
| `cp/delegate` | Sends a prompt to a target selected by name or labels. |
| `cp/delegate_result` | Returns the delegated task result to its caller. |
| `cp/cancel` | Cancels an admitted delegation. |
| `cp/event` | Pushes namespace lifecycle and delegation notifications to observers. |
| `cp/list_agents` | Returns the caller's namespace roster; available to any registered client, including observers. |

The caller creates `delegation_id`, which is the idempotency key. A delegation may include parent references and an absolute `deadline`. If a child deadline exceeds the parent's remaining budget, policy rejects the delegation with `DeadlineExceedsParent`; the server does not clamp it.

After admission, the control plane adds facts clients cannot self-assert:

- **`admission` token** — unique and never reused; required for results, cancellation, and parented delegation.
- **Authenticated `from`** — derived from the credential-bound identity.
- **Full `chain`** — delegation ancestry used for depth and cycle checks.

## Observer Surface (Lobby)

An `observer` is a third identity type, configured with `type = "observer"` in `[[agents]]`. It is a read-only lobby client: the same `cp/register`-first-frame rule and heartbeat lease apply. Observers are never selectable as delegation targets and are unconditionally refused as initiators—no policy override relaxes this.

`cp/event` is a JSON-RPC notification pushed to every observer in a namespace. Event kinds are `agent_registered`, `agent_deregistered`, `delegation_requested`, `delegation_completed`, and `delegation_cancelled`. The envelope is a JSON-RPC 2.0 notification (`method: "cp/event"`, no `id`) whose `params` carry `seq`, `ts`, `namespace`, and flattened event-specific fields. Each namespace has a monotonic, dense `seq`; a gap means the client should resync via `cp/list_agents`. Sequence numbers are not durable across control-plane restarts. Delivery is best-effort through bounded queues, with no replay.

Any registered client can call `cp/list_agents` to fetch its own namespace's roster: name, type, instance ID, labels, and active/max sessions. This is a working Phase 1 read surface, not just a protocol reservation. Intermediate session/turn streaming to observers remains future scope.

Three settings control the surface:

| Setting | Default / behavior |
|---------|--------------------|
| `max_event_excerpt_bytes` | 4096 bytes; validated at no more than 64 KiB. |
| `max_observers_per_namespace` | 16 |
| `[namespaces.<ns>].metadata_only` | `false`; when `true`, events omit prompt/result excerpts, worker error text, and cancel reasons. CP-synthesized diagnostics still appear. |

## Important `cp.toml` Settings

| Setting | Default / behavior |
|---------|--------------------|
| `listen` | `127.0.0.1:9800` |
| `allow_insecure_bind` | Required for non-loopback; use only behind a TLS proxy or on a private network. |
| `max_deadline_secs` | 1800 seconds |
| `max_result_bytes` | 256 KiB; oversized results are truncated keeping the head. |
| `max_frame_bytes` | 1 MiB |
| `max_prompt_bytes` | 256 KiB |
| `max_connections_per_identity` | 8 |
| `max_inflight_delegations` | 4096 |
| `default_max_delegated_sessions_cap` | 16 |
| `[[agents]]` | Immutable identity table: key, namespace, name, and type. |
| `[namespaces.<ns>]` | Policy overrides such as `max_depth` and `allow_worker_initiation`. |

## Authentication and Admission

Clients send `Authorization: Bearer <key>` during the WebSocket upgrade. The key maps server-side to an immutable `[[agents]]` identity. Registration claims must match that binding; a mismatch fails with `IDENTITY_MISMATCH`.

Loopback is the safe default. PR 1/4 already includes control-plane-generated registration handles, atomic admission, non-reusable admission tokens, and per-identity quotas.

## Shipped vs. Coming

**Shipped in PR 1/4:** the standalone `openab-cp` binary and its protocol, config, server, registry, router, and policy implementation.

**Shipped in PR 2/4:** observer identities, sequenced `cp/event` notifications, and the `cp/list_agents` roster inside the CP server—not broker integration.

**Not shipped yet (follow-up slices):**

- OAB-side `[control_plane]` client configuration, runtime connection, and registration
- Agent-facing `spawn_agent`, `check_delegation`, `list_agents`, and `cancel_delegation` MCP facade tools (ADR §7: PR 3/4)
- The Unix-domain-socket, per-session tool injection path; `OPENAB_CP_KEY` must never enter the agent environment
- Control-plane CLI workflows
- Client relay streaming, including intermediate session/turn updates to observers

**Deployment reality:** Nothing connects to this server in a stock deployment; no packaged container image exists yet.

The planned agent tools follow the [MCP Facade](./mcp-facade.md) pattern but are a separate tool set injected through ACP `session/new` `mcpServers`.

## Non-Goals in v1

- No DAG or pipeline engine; orchestration stays in the primary agent's reasoning.
- No durable inbox or offline delivery; both runtimes must be online.
- No session-management primitives yet.
- Worker→worker delegation is protocol-ready but denied by default policy.
- No persistent control-plane state.

This is not a chat adapter and does not replace OpenAB sessions. Adapters remain the human-visible ingress; each receiving runtime still executes delegated work through its own agent/session machinery.

## Further Reading

- Upstream: `docs/control-plane.md`
- Upstream: `docs/adr/agent-control-plane.md`
- Upstream: `crates/openab-cp/cp.toml.example`
- [Multi-Agent](../02-mental-models/multi-agent.md) — visible collaboration versus direct delegation
- [OAB MCP Facade](./mcp-facade.md) — the pattern planned for agent-facing delegation tools
