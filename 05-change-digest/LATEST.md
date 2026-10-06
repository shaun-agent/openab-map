# Latest Change Digest

> Auto-updated. Source range: `3718ef05` → `99c11ec1` (openab `main`)
> **Covers the v0.10.0-beta.5 release (2026-09-26) and everything after it up to the sync SHA.**
> See [`.sync-state`](../.sync-state)

---

## Released: v0.10.0-beta.5 (2026-09-26, PR #1549)

Everything the previous digest flagged as "unreleased — on `main` after beta.4" is now in a
tagged release. Rolled up into beta.5:

- **Control Plane observer/lobby read surface (Phase 1)** — the standalone `openab-cp`
  binary's registry/router/policy plus its observer/lobby read surface are now released.
  Runtime integration, agent-facing tools, CLI, and client relay streaming still pending.
  The [Control Plane](../01-core-concepts/control-plane.md) status line is updated.
- **BREAKING: agy-acp default prompt timeout is 20 minutes** (PR #1534). Pin the old
  behavior back with `[agent.env] AGY_EXTRA_ARGS = "--print-timeout 5m"`.
- **Reverse ACP requests classified before responses** (PR #1540) — stdio ACP frames from
  the agent are matched as agent→client requests first; unknown requests get `-32601` and
  a warn log.
- **MiMoCode CLI pin fix** (PR #1548) — the Docker image's pinned MiMoCode CLI version had
  become unavailable upstream; bumped to an installable one.

**What changed in the map:** [Control Plane](../01-core-concepts/control-plane.md) status
only — the beta.4 feature docs were already accurate.

---

## Feature: Discord `/effort` reasoning-effort slash command

**Commit:** `147deee` — PR #1546

Discord deployments get a slash command to set the agent's reasoning effort per session,
alongside the existing `/models` dropdown. Choices surface from the agent's
`configOptions`, with the effort label shown in pagination.

**What changed in the map:** digest only — slash commands are enumerated in the source's
`docs/slash-commands.md`, which the map intentionally doesn't mirror command-by-command.

---

## Fix: `[[ws:]]` workspace survives hung eviction

**Commit:** `99c11ec` — PR #1557

Hung eviction used to purge `session_workdirs` along with the session's resumable state,
so the replacement session silently started in the default `working_dir` whenever the next
message carried no directive (a cron fire, or any plain follow-up in the thread).
`purge_session_entries()` now leaves the workspace alone; an explicit `/reset` still
forgets it via the new `purge_for_reset()`.

**What changed in the map:** nothing — this makes behavior match what
[Directives](../01-core-concepts/directives.md) and
[Session Lifecycle](../02-mental-models/session-lifecycle.md) already document
(the workspace survives eviction rebuilds; reset forgets it).

---

## Minor

- `739c344` — coding CLI pins bumped to current nightly versions.
- `760ff9c` — clippy clean under Rust 1.99.0 (async-trait 0.1.92, `try_update`).

---

## Status check: openab-pty — graduated from ADR to a live ecosystem

The previous digest said openab-pty was "ADR-only, zero code." **That is no longer true,
and the demand gate is closed.** The work landed outside `openabdev/openab`, in two
sibling repos moving fast (late September → early October 2026):

- [`openabdev/openab-pty`](https://github.com/openabdev/openab-pty) — the sandbox
  runtime: shell sessions in locked-down containers over a WireGuard tailnet, plus the
  `oab-toolchain` sandbox image.
- [`openabdev/instance-mcp`](https://github.com/openabdev/instance-mcp) — the
  computer-side executor, now at **0.8.0 (switchboard mode)**. Highlights in range:
  **reverse attach** (your computer dials INTO the sandbox pod; the pod has zero
  reachability into your tailnet — verified on real hardware), grants that survive a
  daemon restart, tool profiles with full classification (`desktop` documented as
  shell-equivalent; `observe` with a prompt-injection caution), the `mac` → `computer`
  rename, and Linux/Raspberry Pi/headless-Ubuntu hands via a one-core/per-OS-backend
  Rust refactor.
- A **Sandbox Adapter ADR** (instance-mcp, *Proposed*) sketches a `sandbox_*` MCP tool
  family over pluggable backends (OrbStack / k3s / Lambda MicroVMs).
- The end-to-end "cloud brain + thin executor over Tailscale" loop is **openab#1544, an
  open design issue** — direction, not shipped behavior.

**What changed in the map:** new core concept —
[Sandboxes & Computer Grants](../01-core-concepts/computer-grants.md) — covering the
thesis ("a computer is something the agent *calls*, not somewhere it *lives*"), the
reverse-attach trust inversion, tool-profile grants, and the egress-honesty caveat
(no *tailnet* egress; internet egress open by default).
