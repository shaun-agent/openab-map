# Latest Change Digest

> Auto-updated. Source range: `d4f376f6` → `843bb729` (openab `main`)
> **v0.10.0-beta.4 released; Control Plane PR 2/4 is unreleased — on `main` after beta.4.**
> See [`.sync-state`](../.sync-state)

---

## v0.10.0-beta.4 Released

**Commit:** `6b75b559` — chart version bump

Beta.4 captures custom HTTP headers for native MCP servers (#1511), Google Chat ADC authentication and send-once replies (#1513), model-selection docs (#1521), Hermes removal (#1523), and the nightly build channel (#1519/#1522). The header feature is now released; the observer/lobby slice below is not part of beta.4.

> **Deployers using Gemini individual accounts:** Since June 18, 2026, Gemini CLI no longer serves Google AI Pro, Ultra, or free-tier individual accounts. Google recommends migrating to Antigravity CLI. Enterprise Gemini Code Assist licenses and API-key authentication remain supported.

The model-selection docs also cover Antigravity's Discord `/models` dropdown, live `agy models` choices with cache/static fallback, per-session `--model`, and `[pool] default_config_options` defaults.

**What changed in the map:** Updated the release gate in [OAB MCP Facade](../01-core-concepts/mcp-facade.md), Google account routing and model selection in [Which Agent?](../04-decision-trees/which-agent.md), and the current release in [README](../README.md).

---

## Control Plane PR 2/4: Observer/Lobby (Unreleased)

**Commit:** `843bb729` — PR #1470

PR 1/4 shipped the standalone CP server; PR 2/4 adds a working read-only lobby inside that server, not broker integration.

**Key things to know:**
- `observer` joins `primary` and `worker` as an identity type. It follows the same register-first-frame rule and lease, but can never be a delegation target or initiator; no config override permits either.
- `cp/event` pushes `agent_registered`, `agent_deregistered`, `delegation_requested`, `delegation_completed`, and `delegation_cancelled` notifications to every observer in a namespace. Per-namespace `seq` is monotonic and dense; gaps require resync via `cp/list_agents`. Delivery is best-effort with bounded queues, no replay, and no sequence durability across CP restarts.
- `cp/list_agents` lets any registered client fetch its own namespace's roster: name, type, instance ID, labels, and active/max sessions.
- `max_event_excerpt_bytes` defaults to 4096 (maximum 64 KiB); `max_observers_per_namespace` defaults to 16. Per-namespace `metadata_only` defaults to `false`; enabling it omits prompt/result excerpts, worker error text, and cancel reasons from events, but CP-synthesized diagnostics remain.
- OAB-runtime `[control_plane]` connection/registration, agent-facing MCP facade tools (ADR §7: PR 3/4), CLI workflows, and client relay streaming remain pending. Intermediate session/turn streaming to observers is future scope—not the already-working event and roster surface.

**Deployment reality:** Nothing connects to the server in a stock deployment; there is no packaged container image yet.

**What changed in the map:** Expanded [Agent Control Plane](../01-core-concepts/control-plane.md) with the observer surface, seven wire methods, privacy settings, and corrected shipped-vs-pending boundaries.

---

## Removed: Hermes Agent Backend

**PR:** #1523 — included in beta.4

Upstream removed `Dockerfile.hermes`, `docs/hermes.md`, unified/package build targets, all Hermes CI lanes, and entries in `values.yaml`, `config.toml.example`, and README. Flaky `raw.githubusercontent.com` installer fetches were breaking CI for a low-ROI backend.

**What changed in the map:** Removed only the Hermes agent table row from [Which Agent?](../04-decision-trees/which-agent.md). The mandatory OpenClaw + Hermes Agent prior-art requirement is unchanged; [PR Contribution Lifecycle](../03-use-cases/contributing-pr-lifecycle.md) remains untouched.

---

## Minor

- **Nightly channel** (#1519/#1522): per-agent-variant images resolve each vendor's latest CLI fresh daily. Mutable tags are `nightly-<variant>`; immutable tags are `nightly-YYYYMMDD-<runid>.<attempt>-<variant>` (dot-separated attempt, always present). Variants build independently with **no compatibility guarantee**. Excluded: native and agentcore (no CLI), and pi (would be runtime-broken). Release/pre-beta lanes remain SHA-pinned.
- **Google Chat hardening** (#1513): keyless ADC (`[googlechat].use_adc`, `GOOGLE_CHAT_USE_ADC`, Helm `googleChat.useAdc`) uses the attached runtime service account via GCE metadata to impersonate a **distinct, dedicated Chat-app service account** through IAM Credentials `generateAccessToken`, without a key file. `GOOGLE_CHAT_ADC_TARGET_SERVICE_ACCOUNT` (config `adc_target_service_account`) is required with `use_adc=true` and must differ from the runtime SA: Google prohibits self-impersonation (`FAILED_PRECONDITION`), and enabling ADC without a target fails closed. A successfully loaded SA key wins; a configured-but-unloadable key falls back to ADC with a logged identity switch; static token is the last resort. Replies are send-once to avoid 429s/404s under the 1-write/second/space limit; `googlechat` joins `NON_STREAMING_PLATFORMS` (renamed from `NON_EDITABLE_PLATFORMS`). See [Which Adapter?](../04-decision-trees/which-adapter.md).

---

*Next update: triggered by next push to openab/main or daily schedule.*
