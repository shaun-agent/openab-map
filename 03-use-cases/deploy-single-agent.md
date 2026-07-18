# Deploy a Single Agent

The simplest OpenAB deployment: one bot, one platform (Discord), one agent CLI.

## What You'll Have

- A Discord bot that responds in threads
- Backed by an agent CLI (Kiro, Claude Code, etc.)
- Running in Kubernetes via Helm

## Prerequisites

- Kubernetes cluster (or Docker Compose for local)
- Discord bot token (from Discord Developer Portal)
- Agent CLI installed and ACP-compatible
- Helm 3+

## Step 1: Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers)
2. New Application → Bot → Add Bot
3. Enable: **Message Content Intent**, **Server Members Intent**
4. Copy the bot token
5. Invite to your server with permissions: `Send Messages`, `Read Message History`, `Add Reactions`, `Manage Messages`, `Create Public Threads`

Full guide: `docs/platforms/discord.md`

## Step 2: Write config.toml

```toml
[discord]
bot_token = "${DISCORD_BOT_TOKEN}"
allowed_channels = ["YOUR_CHANNEL_ID"]
allow_user_messages = "mentions"    # require @BotName to trigger

[agent]
command = "kiro-cli"
args = ["acp", "--trust-all-tools"]
max_sessions = 10
session_idle_ttl = "24h"
```

Minimal. No hooks, no cron, no secrets management needed for a first deploy.

## Step 3: Create Kubernetes Secret

```bash
kubectl create secret generic openab-secrets \
  --from-literal=DISCORD_BOT_TOKEN="your-token" \
  --from-literal=OPENAI_API_KEY="your-openai-key"
```

## Step 4: Helm Install

```bash
helm repo add openab https://charts.openab.dev
helm repo update

helm install my-bot openab/openab \
  --set agents.main.discord.botToken="${DISCORD_BOT_TOKEN}" \
  --set agents.main.command="kiro-cli" \
  --set-string 'agents.main.discord.allowedChannels[0]=YOUR_CHANNEL_ID'
```

Or with a values file:

```yaml
# values.yaml
agents:
  main:
    command: kiro-cli
    args: [acp, --trust-all-tools]
    discord:
      botToken: "${DISCORD_BOT_TOKEN}"
      allowedChannels: ["YOUR_CHANNEL_ID"]
    env:
      OPENAI_API_KEY: "${OPENAI_API_KEY}"
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
```

```bash
helm install my-bot openab/openab -f values.yaml
```

## Step 5: Test

In your Discord channel:

```
@YourBot what's 2 + 2?
```

You should see:
1. 👀 reaction appears (ack)
2. 🤔 reaction (thinking)
3. A thread is created
4. Bot responds in the thread
5. 👍 reaction on the original message (done)

## Common First-Run Issues

| Symptom | Likely cause |
|---------|-------------|
| No reaction to @mention | Bot token wrong or wrong channel ID |
| 👀 appears but no response | Agent CLI not installed or wrong command |
| Response in channel, not thread | `create_thread` permission missing |
| Responds to all messages, not just mentions | `allow_user_messages` not set |

## What's Next

- [Add a lifecycle hook](./hook-into-lifecycle.md) — git clone a repo at boot
- [Schedule a daily task](./schedule-agent-tasks.md) — cron job to your agent
- [Deploy multiple agents](./deploy-multi-agent.md) — add a second bot
