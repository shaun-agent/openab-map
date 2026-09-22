# Latest Change Digest

> Auto-updated. Source range: `843bb729` → `3718ef05` (openab `main`)
> **Unreleased — on `main` after v0.10.0-beta.4.**
> See [`.sync-state`](../.sync-state)

---

## Breaking: agy-acp default prompt timeout is now 20 minutes

**Commit:** `50424ed4` — PR #1534

The Antigravity adapter (`agy-acp`) now supplies `--print-timeout 20m` on every prompt invocation instead of inheriting the CLI's own default (5 minutes at the time the issue was diagnosed). Long tasks no longer die with `Error: timeout waiting for response` at the 5-minute mark.

**Key things to know:**
- An explicit `--print-timeout <duration>` (or `--print-timeout=<duration>`) in `AGY_EXTRA_ARGS` is preserved — the adapter only injects the 20m default when you haven't set one.
- Migration back to the old behavior: `[agent.env] AGY_EXTRA_ARGS = "--print-timeout 5m"`.
- The timeout stays finite — tasks exceeding the configured duration still fail. This controls the CLI print timeout only, not other OpenAB timeouts.

**What changed in the map:** digest only — the [Which Agent?](../04-decision-trees/which-agent.md) guidance is unaffected.

---

## Fix: reverse ACP requests classified before responses

**Commit:** `3718ef05` — PR #1540

On the stdio ACP client path (OpenAB ↔ agent subprocess), inbound frames from the agent are now classified as agent→client *requests* before being treated as responses. Previously a reverse request could be misrouted as a response when JSON-RPC ids collided (a `JsonRpcId` quirk: untagged deserialization puts every non-negative integer in `Unsigned`, so `Unsigned(5) != Signed(5)` structurally — correlation now goes through `as_u64()`).

**Key things to know:**
- `session/request_permission` keeps its existing auto-reply behavior (see [ACP](../01-core-concepts/acp.md), tool call auto-reply).
- Any other agent→client request is answered with JSON-RPC `-32601` and now logged at warn level — OpenAB advertises `clientCapabilities: {}`, so such a request means the agent is calling a capability OpenAB never offered.

**What changed in the map:** digest only — no documented behavior changed.

---

## Status check: openab-pty

Still **ADR-only, zero code** — no `openab-pty` crate exists in the tree and the ADR was untouched this range. The demand gate (≥3 independent user requests within 90 days) remains open.

---

*Next update: triggered by next push to openab/main or daily schedule.*
