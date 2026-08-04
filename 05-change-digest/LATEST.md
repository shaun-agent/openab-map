# Latest Change Digest

> Auto-updated. Source range: `9672700` → `3ace7de3` (openab `main`)
> **Unreleased on `main` after v0.10.0-beta.2 — expected in the next beta.**
> See [`.sync-state`](../.sync-state)

---

## New subsystem: OAB MCP Facade

**PRs:** #1448, #1453, #1454, #1450, #1446

OpenAB now has a loopback Streamable HTTP MCP facade that presents every configured downstream provider through only `search_capabilities` and `execute_capability`. Providers come from layered `mcp.json`; filters, JSON-Schema validation, timeouts, secret redaction, and `mcp.audit` logging apply before native downstream `tools/call` dispatch.

**Key things to know:**
- `[mcp]` enables `127.0.0.1:8848/mcp`; non-loopback binds are refused, and a config containing only `[mcp]` supports facade-only `openab run` deployments.
- The facade has no general auth layer. The host or pod is the trust boundary, while session-bound sources require the broker-minted `OPENAB_SESSION_TOKEN` bearer.
- OpenAB writes `.openab/mcp-facade.json` but never edits a coding CLI's own MCP settings.
- `mcp.audit` is a bare tracing target: `RUST_LOG=openab=debug` misses it unless `mcp.audit=info` is added explicitly.
- It complements rather than replaces octobroker: pod-level personal capabilities can include fleet-level octobroker as a downstream.

**What changed in the map:**
- Added [OAB MCP Facade](../01-core-concepts/mcp-facade.md).
- Added both new network surfaces to [Trust Model](../01-core-concepts/trust-model.md).
- Added the facade to the [What is OpenAB?](../00-what-is-openab.md) architecture.

---

## New: Browser control via MCP-over-ACP tunnel

**PR:** #1447

ACP clients can now publish `type: "acp"` MCP servers over the existing `/acp` WebSocket. The katashiro browser extension uses the reverse tunnel to provide five DOM-semantic tools—read DOM, screenshot, navigate, click, and type—which the agent discovers as session-aware `openab-browser` capabilities behind the facade.

**Key things to know:**
- Browser control requires `[mcp]`; without it, nothing starts.
- Agent-to-client request routing exists only as tunnel plumbing. General permission relay, structured tool updates, progressive streaming, and effective backend cancellation remain open.
- The frame cap is now 8 MiB overall for screenshots, while method-bearing frames remain limited to 1 MiB.
- Proxy mode and `openab browser-bridge` / `OPENAB_BROWSER_MODE` were removed before merge. The facade is the only delivery path.
- The canonical ADR is now `docs/adr/acp-server-websocket-reverse-mcp.md`; the earlier browser ADR path was deleted.

**What changed in the map:**
- Added [Let Your Agent Drive the Browser](../03-use-cases/browser-control-from-chat.md).
- Updated [Drive Your Agent from an ACP Client](../03-use-cases/drive-agent-from-acp-client.md) with the tunnel, limits, and remaining roadmap.
- Updated [ACP](../01-core-concepts/acp.md) and fixed its ADR link.

---

## New: Native Gmail adapter

**PRs:** #1449, #1455

The hosted `gmailmcp.googleapis.com` route was abandoned because it requires Workspace Developer Preview enrollment and rejects consumer accounts. The native adapter instead serves six read/draft-only tools over Gmail's GA REST API: `search_threads`, `get_thread`, `get_message`, `list_labels`, `list_drafts`, and `create_draft`; it never sends mail.

Use `openab mcp gmail-native login` for paste-back OAuth and `openab mcp gmail-native serve --listen 127.0.0.1:8850` for development. `GMAIL_OAUTH_CLIENT_ID` is required, while `GMAIL_OAUTH_CLIENT_SECRET` is optional in code for public clients. Google's Web and Desktop client types are both issued a secret and require it at the token endpoint, so in practice set both. The refresh token is stored under `gmail-native` in `~/.openab/agent/auth.json` with mode 0600. The recommended production shape registers all six tools behind the facade with an explicit include filter.

**What changed in the map:** [OAB MCP Facade](../01-core-concepts/mcp-facade.md) documents Gmail as a downstream and links the upstream guide.

---

## New platform: LINE WORKS

**PR:** #1456

LINE WORKS joins the gateway tier with signed webhook receipt and REST sends. It supports flat 1:1 talks and channels, inbound image/audio/file attachments, audio-attachment STT, flexible-template rich messages, and receipt acknowledgements; outbound file upload is not implemented. It has no threads, reactions, or message editing; streaming is forced off. User access remains deny-all unless explicitly allowed.

**What changed in the map:** Added LINE WORKS to [Adapters](../01-core-concepts/adapters.md) and [Which Adapter?](../04-decision-trees/which-adapter.md), including its capability constraints.

---

## Docs: CLI conventions

**PR:** #1452

Top-level verbs act on the bot itself (`run`, `setup`, `set`, `get`), while noun namespaces act on subsystems (`openab mcp <addon> <action>`). Production serving is config-driven; namespace `serve` subcommands are for development only.

**What changed in the map:** The convention is summarized in [OAB MCP Facade](../01-core-concepts/mcp-facade.md).

---

*Next update: triggered by next push to openab/main or daily schedule.*
