# Schedule Agent Tasks

OpenAB has a built-in config-driven cron scheduler. No external K8s CronJob or GitHub Actions needed for simple periodic prompts.

## The Model

At the scheduled time, OpenAB sends a message to a channel as if a user typed it. The agent responds in a thread. One tick per minute; matched jobs fire immediately.

```toml
[[cron.jobs]]
schedule    = "0 9 * * 1-5"
channel     = "123456789012345678"   # must be in allowed_channels
message     = "Summarize yesterday's merged PRs."
platform    = "discord"              # optional if only one platform configured
sender_name = "DailyOps"            # display name shown in the thread
timezone    = "Asia/Taipei"
```

## Full Field Reference

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `schedule` | Yes | — | 5-field POSIX cron expression |
| `channel` | Yes | — | Platform channel/chat ID |
| `message` | Yes | — | Text sent to the agent |
| `platform` | No | auto | `"discord"`, `"slack"`, etc. Required when multiple platforms are configured |
| `sender_name` | No | — | Display name for the synthetic sender |
| `timezone` | No | UTC | IANA timezone (e.g. `"Asia/Taipei"`, `"America/New_York"`) |
| `id` | No | — | Unique ID — required for goal-driven auto-disable |
| `enabled` | No | `true` | Set to `false` to disable without removing |

## Cron Syntax

```
minute  hour  day-of-month  month  day-of-week
  0      9         *           *       1-5
```

| Field | Range | Wildcards |
|-------|-------|----------|
| minute | 0-59 | `*`, `,`, `-`, `*/n` |
| hour | 0-23 | `*`, `,`, `-`, `*/n` |
| day-of-month | 1-31 | `*`, `,`, `-` |
| month | 1-12 | `*`, `,`, `-` |
| day-of-week | 0-7 (0=Sun) | `*`, `,`, `-` |

---

## Usercron — Hot-Reload Without Redeploy

Regular `[[cron.jobs]]` in `config.toml` requires a redeploy to change. **Usercron** reads from a separate file that's watched and reloaded live.

Enable it in `config.toml`:

```toml
[cron]
usercron_enabled = true
usercron_path    = "cronjob.toml"   # relative to $HOME/.openab/
```

Then create `~/.openab/cronjob.toml`:

```toml
[[jobs]]
schedule    = "*/10 * * * *"
channel     = "1490282656913559673"
message     = "Check CI status and report any failures."
platform    = "discord"
sender_name = "CIBot"
timezone    = "Asia/Taipei"
```

Edit the file → scheduler reloads automatically. No redeploy needed.

**This means an agent can manage its own schedule.** A user can say "set up a cronjob to check CI every 10 minutes" — the agent writes to `~/.openab/cronjob.toml` and the scheduler picks it up immediately.

---

## Goal-Driven Auto-Disable

A job can check a success condition after each run and automatically disable itself when the goal is met.

```toml
[[jobs]]
id      = "fix-unit-tests"
enabled = true
schedule = "*/10 * * * *"
channel  = "1490282656913559673"
message  = "Unit tests still failing. Continue fixing."

# Run this command after the agent responds:
disable_on_success             = "npm test && echo OPENAB_GOAL_SUCCESS"
disable_on_success_match       = "OPENAB_GOAL_SUCCESS"
disable_on_success_timeout_secs = 120
disable_on_success_working_dir  = "/workspace/my-project"
```

When `disable_on_success` exits and its stdout contains `disable_on_success_match`, the scheduler writes `enabled = false` into the usercron file. The job stops firing.

**Use cases:**
- Keep retrying a failing test suite until it passes
- Poll an external API until a condition is met
- Run a migration until it completes successfully

---

## Helm Deployment

```yaml
agents:
  kiro:
    cronjobs:
      - schedule:    "0 9 * * 1-5"
        channel:     "123456789012345678"
        message:     "Summarize yesterday's merged PRs."
        senderName:  "DailyOps"
        timezone:    "Asia/Taipei"
```

> **Tip:** Channel IDs are large integers. Use `--set-string` to prevent Helm from treating them as floats:
> ```bash
> helm install ... --set-string 'agents.kiro.cronjobs[0].channel=123456789012345678'
> ```

---

## When to Use External Schedulers

| Need | Use |
|------|-----|
| Simple periodic prompt | Built-in cron |
| Agent manages its own schedule | Usercron |
| Goal-driven retry loop | Usercron + `disable_on_success` |
| Task runs longer than ~5 minutes | K8s CronJob |
| Retry logic, conditional branching | GitHub Actions / Step Functions |
| Multi-step DAG | GitHub Actions / Step Functions |

---

## How Cron Messages Are Delivered

Cron messages bypass dispatch mode — always their own ACP turn, never batched with user messages. If the channel has an active session when the job fires, the message goes to that session. If not, a new session is created.

---

## Common Patterns

**Daily standup:**
```toml
[[cron.jobs]]
schedule = "0 9 * * 1-5"
message  = "Daily standup: what is in progress, what is blocked, what shipped yesterday?"
timezone = "Asia/Taipei"
```

**PR review reminder:**
```toml
[[cron.jobs]]
schedule = "0 10,15 * * 1-5"
message  = "Check for PRs waiting more than 24 hours for review and ping the relevant people."
```

**Weekend infrastructure check:**
```toml
[[cron.jobs]]
schedule = "0 8 * * 6,0"
message  = "Weekend health check: summarize alerts, anomalies, or cost spikes from the past 48 hours."
```

**Self-healing loop (usercron):**
```toml
[[jobs]]
id      = "fix-flaky-e2e"
enabled = true
schedule = "*/15 * * * *"
message  = "E2E tests are still flaky. Investigate and fix the root cause."
disable_on_success             = "npm run e2e && echo OPENAB_GOAL_SUCCESS"
disable_on_success_match       = "OPENAB_GOAL_SUCCESS"
disable_on_success_timeout_secs = 300
disable_on_success_working_dir  = "/workspace/app"
```

---

## Further Reading

- Source: `crates/openab-core/src/cron.rs`
- Docs: `docs/cronjob.md`
