# Latest Change Digest

> Auto-updated. Source range: `2e3292b` → `6859733` (openab `main`)
> See [`.sync-state`](../.sync-state)

---

## v0.9.0 Released + v0.10.0-beta.1 Tagged

openab hit its v0.9.0 stable release in this window and immediately tagged v0.10.0-beta.1.

---

## New: Kimi Code CLI Backend

**Commit:** `654bf97` — feat: add Kimi Code CLI backend

Kimi Code (`kimi acp`) from Moonshot AI is now a supported agent backend. It speaks ACP natively — no adapter needed.

**What changed in the map:** [Which Agent?](../04-decision-trees/which-agent.md) updated with Kimi in the decision tree and quick-reference table.

**Key things to know:**
- Command: `kimi acp`, working dir `/home/node`
- Auth: interactive — run `kimi` and enter `/login` inside the container
- Supports multiple LLM providers via `~/.kimi-code/config.toml` (Kimi/Moonshot, Anthropic, OpenAI-compatible, Gemini, Vertex AI)
- Provider credentials must be in Kimi's own config — not in OpenAB's `[agent].env`
- Helm image tag: `openab:<tag>-kimi`
- Full guide: `docs/kimi.md`

---

## New: xAI / SuperGrok / X Premium OAuth in openab-agent

**Commit:** `7faa937` — feat(openab-agent): xAI subscription login via device-code OAuth

The native `openab-agent` now supports signing into xAI with a SuperGrok or X Premium subscription — no API key required.

**What changed in the map:** [Which Agent?](../04-decision-trees/which-agent.md) updated with xAI OAuth notes in the openab-agent section.

**Key things to know:**
- Run `openab-agent auth xai` for device-code flow (works headless via `kubectl exec`)
- Tokens stored in `~/.openab/agent/auth.json`, auto-refreshed
- Select with `OPENAB_AGENT_PROVIDER=xai` or `OPENAB_AGENT_MODEL=xai/grok-4.5`
- xAI is **not** auto-detected — you must explicitly select it
- `OPENAB_AGENT_XAI_MODEL` (default `grok-4.5`) and `OPENAB_AGENT_XAI_BASE_URL` are new env vars
- Config resolution precedence clarified: `OPENAB_AGENT_PROVIDER` > model prefix in env > model prefix in `config.json` > auto-detect

---

## New: Review Contract (contributor workflow)

**Commit:** `f8e9156` — docs(review): add Review Contract policy

Every PR to openab must now include a `## Review Contract` section with: Goal, Non-goals, Accepted Residual Risks, Acceptance Criteria, and Follow-ups. A GitHub Actions workflow validates structure automatically.

**Impact on contributors:**
- Mandatory for all PRs (except those labelled `review-contract-exempt` by a maintainer)
- Round 1 is a full review + contract freeze; later rounds are incremental
- Post-freeze blockers must pass the Late Blocker Gate (concrete evidence of broken acceptance criteria, unachieved goal, or new correctness/security/data-loss defect)
- Full policy: `docs/review-contract.md`

---

## Minor: Grok CLI version bump

`chore: upgrade Grok CLI to version 0.2.106` — no user-facing behavior change.

---

*Next update: triggered by next push to openab/main or daily schedule.*
