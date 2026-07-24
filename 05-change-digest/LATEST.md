# Latest Change Digest

> Auto-updated. Source range: `6859733` → `9672700` (openab `main`)
> See [`.sync-state`](../.sync-state)

---

## v0.10.0-beta.2 Released

The Helm chart `version` and `appVersion` moved from v0.10.0-beta.1 to v0.10.0-beta.2. This release captures the ACP WebSocket server and Feishu unified-mode WebSocket fix below.

---

## New: OpenAB is now an ACP Server — WebSocket `/acp` endpoint

**Commit:** `2c5b549` — [PR #1418](https://github.com/openabdev/openab/pull/1418)

OpenAB now accepts standard ACP clients over `GET /acp`, reversing its historical client-only direction while preserving the existing stdio path to agent subprocesses.

**Key things to know:**
- Both `openab-gateway` and unified `openab run` serve JSON-RPC 2.0 over WebSocket with subprotocol `acp.v1`.
- Enable it with the `acp` Cargo feature and `OPENAB_ACP_ENABLED=true`; `acp` is included in `unified`.
- Authentication is fail-closed: non-loopback binds require `OPENAB_ACP_AUTH_KEY`, while browser keyless access also requires an exact `OPENAB_ACP_ALLOWED_ORIGINS` match.
- ACP traffic uses synthetic sender `acp_client`, which must pass broker identity admission.
- Phase 1 supports `initialize`, `session/new`, `session/resume`, `session/prompt`, text `session/update`, and partial `session/cancel`; agent-to-client requests and other method families are deferred.
- `session/resume` returns `{}` immediately for any well-formed `sess_<uuid>` without checking liveness or replaying history. If the four-hour-default pool TTL has expired the session, the next prompt starts fresh and its first reply carries a `Session expired` prefix.
- Limits are 128 sessions per connection, 32 in-flight prompts, and 1 MiB inbound frames.
- Phase 2 targets permission requests, progressive streaming, structured `tool_call` updates, and MCP-over-ACP; Phase 3 and later add history replay, thought chunks and plans, richer content, fs/terminal methods, session administration, and Streamable HTTP.

**What changed in the map:**
- Added [Drive Your Agent from an ACP Client](../03-use-cases/drive-agent-from-acp-client.md).
- Reframed [ACP](../01-core-concepts/acp.md) around OpenAB's client and server roles.
- Extended the [What is OpenAB?](../00-what-is-openab.md) architecture diagram.
- Clarified the non-chat endpoint in [Adapters](../01-core-concepts/adapters.md).
- Added ACP guidance to [Which Adapter?](../04-decision-trees/which-adapter.md).
- Added the endpoint to [Deployment Topology](../02-mental-models/deployment-topology.md).

---

## Fix: Feishu WebSocket now starts in unified mode

**Commit:** `421f3ce` — PR #1443

Unified `openab run` previously mounted only the Feishu webhook route and never started the WebSocket long-connection client. Because `FEISHU_CONNECTION_MODE=websocket` is the default, unified deployments using that default received no events.

The unified binary now starts the WebSocket client, with a bounded 15-second bot-identity resolution timeout, graceful shutdown, and a card-streaming idle reaper. Upstream `docs/feishu.md` now gates Unified Mode at v0.9.0+ and WebSocket support at v0.10.0+.

**Map impact:** None beyond this digest; the map never documented the broken behavior.

---

## New: Maintainer take-over policy for fork PRs

**Commit:** `136554e` — PR #1444

When a fork PR needs only small mechanical fixes after direction is accepted, or its contributor becomes unresponsive, a maintainer may move the work to an in-repo branch. Attribution must be preserved through contributor commits or a `Co-authored-by` trailer, the replacement PR must credit the contributor and link the superseded PR, and the original must close with credit. Contributors can always choose to finish the work themselves.

PR #1443 taking over #1440 is the live example.

**What changed in the map:** [E2E PR Lifecycle](../03-use-cases/contributing-pr-lifecycle.md) now summarizes the policy.

---

## Minor: fork-PR label writes moved to hourly reconciliation

**Commit:** `fc22758` — PR #1442

GitHub App tokens are read-only for `pull_request_review` events from forks, so immediate label writes were failing with 403. The label-writing job now runs immediately only for same-repository branches; fork PRs rely on the existing hourly reconciliation job and may show up to about one hour of label lag.

**What changed in the map:** [E2E PR Lifecycle](../03-use-cases/contributing-pr-lifecycle.md) now calls out the delay.

---

*Next update: triggered by next push to openab/main or daily schedule.*
