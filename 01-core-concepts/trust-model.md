# Trust Model — Identity and Access Control

OpenAB's trust model has three layers: who can send messages, which bots can talk to each other, and how credentials are isolated. Getting this wrong lets untrusted users command your agent. Getting it right is the difference between a team tool and a public attack surface.

## Layer 1 — Channel Allowlist

OpenAB ignores messages from channels not in the allowlist:

```toml
[discord]
allowed_channels = ["123456789012345678", "987654321098765432"]
```

Messages from any other channel are silently dropped. This is the coarsest gate — it runs before any user identity check.

## Layer 2 — User Message Policy

Controls when human users need to @mention the bot:

```toml
[discord]
allow_user_messages = "multibot-mentions"  # default
# Options:
#   "all"               — respond to all messages in allowed channels
#   "mentions"          — always require @mention
#   "involved"          — require @mention only if bot hasn't spoken in the thread
#   "multibot-mentions" — require @mention only when 2+ bots are present
```

`"multibot-mentions"` is the recommended production setting. It keeps single-bot threads natural (no @mention spam) while preventing accidental triggering when multiple bots share a channel.

## Layer 3 — Bot Message Policy

Controls whether OpenAB responds to messages from other bots (critical for multi-agent setups):

```toml
[discord]
allow_bot_messages = "mentions"   # require explicit @mention from bots
trusted_bot_ids = ["BOT_ID_1", "BOT_ID_2"]  # only these bots can trigger responses
max_bot_turns = 100               # consecutive bot→bot turn cap (hard limit: 1000)
```

| `allow_bot_messages` value | Behavior |
|---------------------------|---------|
| `"off"` | Ignore all bot messages (default, safest) |
| `"mentions"` | Only respond if explicitly @mentioned by a bot |
| `"all"` | Respond to all bot messages (capped by `max_bot_turns`) |

`max_bot_turns` prevents infinite bot loops. A human message resets the counter. The compiled-in hard cap is 1000 — there is no config value that overrides this.

## Credential Isolation

All secrets are resolved in the OpenAB process. Nothing is passed to agents.

```
config.toml:
  ANTHROPIC_API_KEY = "aws-sm://prod/secrets#anthropic_key"
                              ↓
              OpenAB resolves at boot
                              ↓
  env for agent subprocess:
  HOME=/home/openab
  PATH=/usr/local/bin:/usr/bin:/bin
  USER=openab
  (no ANTHROPIC_API_KEY — agent doesn't need it, OpenAB holds it)
```

Agents call the LLM through their own auth, not through OpenAB. The secrets OpenAB holds are for its own operations (bot tokens, S3 access, etc.).

## Sandbox Requirements

For production, OpenAB **must** run inside a container or pod:

```yaml
# Kubernetes securityContext (from Helm chart)
securityContext:
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
```

OpenAB doesn't enforce this itself — that's the deployment layer's job. Running OpenAB bare-metal in production (without a container) is explicitly unsupported and violates the security model.

## Secret Providers

| Provider | Syntax | Use case |
|---------|--------|---------|
| AWS Secrets Manager | `aws-sm://secret-id#json-key` | Production K8s / ECS |
| Exec provider | `exec:///path/to/script key attr` | HashiCorp Vault, custom |
| Plain value | literal string | Development only |

Missing secrets cause a hard exit at boot — fail-closed, never fail-open.

## Thread Ownership (Future)

A planned feature: only the user who started a thread can `/reset` it or transfer it to another bot. Not yet enforced — currently any user in the channel can reset any thread.

## Further Reading

- Source: `crates/openab-core/src/trust.rs`
- Source: `crates/openab-core/src/secrets.rs`
- Docs: `docs/secrets-management.md`
- [Multi-Agent](../02-mental-models/multi-agent.md) — bot trust in practice
