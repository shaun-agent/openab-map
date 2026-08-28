# Latest Change Digest

> Auto-updated. Source range: `280db4db` → `d4f376f6` (openab `main`)
> **Unreleased — on `main` after v0.10.0-beta.3.**
> See [`.sync-state`](../.sync-state)

---

## New: Custom HTTP headers for native MCP servers

**Commit:** `d4f376f6` — PR #1511

HTTP server entries in layered `mcp.json` can now define a `headers` map, including credentials sourced from the environment:

```json
"headers": { "X-API-Key": "${env:REMOTE_MCP_API_KEY}" }
```

**Key things to know:**
- `${env:VAR}` interpolation applies to values only; header names are literal and case-insensitive, with case-variant duplicates rejected.
- Transport-owned `Accept`, `MCP-Session-Id`, and `Last-Event-ID` are rejected before connection. `MCP-Protocol-Version` is accepted but replaced by the negotiated version.
- Malformed headers or missing environment variables fail only the affected server, do not charge its circuit breaker, and do not stop other providers.
- Automatic HTTP redirects are disabled for MCP and OAuth requests, preventing custom credentials from being replayed to a redirect target.

**What changed in the map:** Added the custom-header configuration and security rules to [OAB MCP Facade](../01-core-concepts/mcp-facade.md).

---

## Minor

- **Test hygiene** (`8661f3f8`, PR #1506): replaced real-looking ARN strings in parsing tests with example values; no runtime or architectural behavior changed.

---

*Next update: triggered by next push to openab/main or daily schedule.*
