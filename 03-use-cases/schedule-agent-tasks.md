# Schedule Agent Tasks

Use OpenAB's built-in cron to send messages to your agent on a schedule — no external scheduler needed.

## The Model

Cron jobs are defined in `config.toml`. At the scheduled time, OpenAB sends a message to a specified channel as if a user typed it. The agent responds in a thread.

```toml
[[cron.jobs]]
schedule = "0 9 * * 1-5"             # 9am Monday-Friday
channel = "123456789012345678"         # channel ID (must be in allowed_channels)
message = "Summarize yesterday's PRs and flag anything that needs review."
timezone = "America/New_York"
```

## Cron Syntax

Standard 5-field POSIX cron:

```
minute  hour  day-of-month  month  day-of-week
  0      9         *           *       1-5
```

| Field | Range | Wildcards |
|-------|-------|----------|
| minute | 0-59 | `*`, `,`, `-` |
| hour | 0-23 | `*`, `,`, `-` |
| day-of-month | 1-31 | `*`, `,`, `-` |
| month | 1-12 | `*`, `,`, `-` |
| day-of-week | 0-7 (0=Sun, 7=Sun) | `*`, `,`, `-` |

## Multiple Jobs

```toml
[[cron.jobs]]
schedule = "0 9 * * 1-5"
channel = "123456789012345678"
message = "Morning standup: what did we ship yesterday?"
timezone = "America/New_York"

[[cron.jobs]]
schedule = "0 17 * * 5"
channel = "123456789012345678"
message = "Weekly summary: top 5 achievements this week, key blockers, plans for next week."
timezone = "America/New_York"

[[cron.jobs]]
schedule = "0 */6 * * *"
channel = "987654321098765432"
message = "Check deployment health and alert if any service is degraded."
timezone = "UTC"
```

## How Cron Messages Are Delivered

Cron messages bypass dispatch mode — they're always delivered as their own ACP turn, not batched with user messages. The agent sees them as if a user sent them, with a synthetic sender ID.

If the channel has an active session (thread) when the cron fires, the message goes to that session. If not, a new session is created.

## Timezone Configuration

Without `timezone`, cron fires in UTC. Always specify timezone for business-hour schedules:

```toml
timezone = "America/New_York"    # US Eastern
timezone = "Europe/Berlin"       # Central European
timezone = "Asia/Tokyo"          # JST
timezone = "Asia/Taipei"         # CST (Taiwan)
```

Valid timezone strings are IANA timezone identifiers.

## Common Patterns

**Daily standup:**
```toml
[[cron.jobs]]
schedule = "0 9 * * 1-5"
message = "Daily standup: what's in progress, what's blocked, what shipped yesterday?"
```

**PR review reminder:**
```toml
[[cron.jobs]]
schedule = "0 10,15 * * 1-5"
message = "Check for PRs waiting more than 24 hours for review and ping the relevant people."
```

**Weekend infrastructure check:**
```toml
[[cron.jobs]]
schedule = "0 8 * * 6,0"
message = "Weekend health check: summarize any alerts, anomalies, or cost spikes from the past 48 hours."
```

**End-of-sprint retrospective prompt:**
```toml
[[cron.jobs]]
schedule = "0 16 * * 5"   # every Friday
message = "Retrospective prompts: what slowed us down this sprint? what should we try next sprint?"
```

## Further Reading

- Source: `crates/openab-core/src/cron.rs`
- Docs: `docs/cronjob.md`
