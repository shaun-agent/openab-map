# Latest Change Digest

> Auto-updated. Source range: `3ace7de3` → `280db4db` (openab `main`)
> See [`.sync-state`](../.sync-state)

---

## v0.10.0-beta.3 Released

**Commit:** `d64c678f` — PR #1466

The v0.10.0-beta.3 tag is a chart `version` and `appVersion` bump, but its ancestry makes the previous feature wave officially released:

- OAB MCP Facade
- Browser control through MCP-over-ACP
- LINE WORKS gateway adapter
- Native Gmail adapter

**What changed in the map:** Removed stale unreleased-on-main gates and marked these features as released in v0.10.0-beta.3 throughout the map.

---

## New: Agent Control Plane (`openab-cp`) — PR 1/4

**ADR:** `448b05fb` — PR #1465

**Code:** `94354a75` — PR #1469

The accepted Agent Control Plane design adds a direct, structured route for agent-to-agent delegation. Where the gateway routes human↔agent messages, the control plane routes agent↔agent messages without Discord rate limits, platform latency, formatting constraints, or orchestration noise in human channels. Chat-based bot collaboration remains the human-visible option rather than being replaced.

PR 1/4 ships only the standalone `openab-cp` binary:

- A registry with 15-second heartbeats and 45-second lease expiry
- Routing by agent name or labels to live, non-saturated runtimes
- Namespace-authoritative policy for initiation, depth, cycles, and cross-namespace calls
- JSON-RPC-style `cp/register`, `cp/delegate`, `cp/delegate_result`, and `cp/cancel` frames over authenticated WebSocket
- Server-bound identity, atomic admission, non-reusable admission tokens, ancestry chains, and per-identity quotas

Broker-side `[control_plane]` integration, the agent-facing delegation MCP tools, and CLI workflows remain PRs 2–4. **ADR accepted; PR 1/4 shipped, but the subsystem is unreleased—on `main` after v0.10.0-beta.3.**

**What changed in the map:** Added [Agent Control Plane](../01-core-concepts/control-plane.md) and contrasted direct delegation with chat-platform b2b in [Multi-Agent](../02-mental-models/multi-agent.md).

---

## Proposed: `openab-pty` remote terminal runtime (ADR-only)

**ADRs:** `2395ea1b` — PR #1478; revised by `280db4db` — PR #1480

`openab-pty` is a proposed separate binary for remote, sandboxed raw-terminal access to coding CLIs in Kubernetes workspaces that survive laptop loss. It supersedes the rejected in-process PTY Mode design and defines three profiles:

1. **ACP only** — today's default, unchanged.
2. **PTY only** — standalone remote terminal and the MVP scope.
3. **ACP + PTY sidecar** — a demand-gated target design, not MVP; MVP always uses separate pods.

The revised kill domain has two tiers: process-group termination plus subreaper/pidfd cleanup by default, with possible escapees audited until pod replacement; optional per-session cgroup v2 `cgroup.kill` hardening gives zero-survivor convergence when subtree delegation is available. Missing cgroup support fails closed only when Tier 2 is explicitly requested.

Administration is remote-only on the authenticated public listener. There is no in-container admin socket or operator CLI for an escaped process to attack; the bootstrap credential is at least 256 random bits and only its hash is stored. RWO storage can support adjacent pods pinned to one node—RWX/EFS is not inherently required.

The `!` marker records a breaking revision to prior ADR commitments, not shipped code: mandatory Phase-1 cgroups and the in-container operator CLI were withdrawn. The ADR remains **Proposed**, implementation is gated on at least three independent requests within 90 days plus budget, and there is zero code or workspace crate today.

**What changed in the map:** Digest only. A concept page is deliberately deferred until implementation ships.

---

## Minor

- **Platform-schema CI hardening** (`62453ac7`, PR #1462): preserves the open contribution model, triggers conformance checks on adapter source changes plus a weekly backstop, and strengthens code-reference validation. No platform capability facts changed.
- **agy CLI pin** (`6f1c530c`): bumped 1.1.4 → 1.1.13 with no architectural impact.

---

*Next update: triggered by next push to openab/main or daily schedule.*
