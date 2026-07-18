# Deploy Multiple Agents

Two or more bots in the same channel, each backed by a different agent CLI, coordinating through the platform.

## The Model

Each agent is an independent pod with its own:
- Discord bot token (registered as separate bot applications)
- Session pool
- ACP subprocess fleet
- `allow_bot_messages` policy

They share: the Discord channel. Coordination is via messages, not via any shared infrastructure.

## Step 1: Register Two Discord Bots

In the Discord Developer Portal, create two separate applications:
- `KiroBot` — token: `BOT_TOKEN_KIRO`
- `ClaudeBot` — token: `BOT_TOKEN_CLAUDE`

Both invited to the same server and channel with identical permissions.

## Step 2: Helm values for multi-agent

```yaml
# values.yaml
agents:
  kiro:
    command: kiro-cli
    args: [acp, --trust-all-tools]
    discord:
      botToken: "${BOT_TOKEN_KIRO}"
      allowedChannels: ["YOUR_CHANNEL_ID"]
      allowUserMessages: "multibot-mentions"   # require @mention when 2+ bots active
      allowBotMessages: "mentions"             # only respond to explicit @KiroBot
      trustedBotIds: ["CLAUDE_BOT_DISCORD_ID"] # only Claude can trigger it
      maxBotTurns: 10
    env:
      OPENAI_API_KEY: "${OPENAI_API_KEY}"

  claude:
    command: claude-agent-acp
    discord:
      botToken: "${BOT_TOKEN_CLAUDE}"
      allowedChannels: ["YOUR_CHANNEL_ID"]
      allowUserMessages: "multibot-mentions"
      allowBotMessages: "off"    # Claude only responds to humans, not to Kiro
    env:
      ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"
```

```bash
helm install team-bots openab/openab -f values.yaml
```

This creates two separate Deployments in Kubernetes — one per agent.

## Step 3: Verify Bot Isolation

```
@KiroBot write me a draft for feature X
```

KiroBot responds. ClaudeBot ignores (no @mention, `allow_bot_messages = "off"`).

```
@ClaudeBot review KiroBot's response above
```

ClaudeBot responds. KiroBot ignores (no @mention to KiroBot).

## Multi-Agent Review Pattern

For intentional b2b pipelines where Kiro drafts and Claude reviews:

```yaml
agents:
  kiro:
    discord:
      allowBotMessages: "mentions"
      trustedBotIds: ["CLAUDE_BOT_ID"]
      maxBotTurns: 5   # tight cap — review loop should be short

  claude:
    discord:
      allowBotMessages: "off"   # one-way: Claude reviews but doesn't trigger further loops
```

Flow:
1. Human asks Kiro to draft
2. Kiro drafts, tags Claude: `@ClaudeBot review this [[reply_to:KIRO_MSG_ID]]`
3. Claude reviews, sends feedback to thread
4. Kiro sees @mention, incorporates feedback
5. Human approves (or loop exits via `maxBotTurns`)

## Gotchas

**Both bots respond to the same message**

Check `allow_user_messages`. With `"multibot-mentions"`, both bots require explicit @mention once they've both spoken in the channel. Without it, both might respond to any channel message.

**Infinite loop**

If both bots have `allow_bot_messages = "all"` and one mentions the other, they'll loop until `max_bot_turns` hits. Use `"mentions"` not `"all"` unless you're building a deliberate pipeline.

**Wrong bot responds**

`trusted_bot_ids` is how you limit which bots can trigger which other bots. If you don't set it, any bot can trigger any bot (subject to `allow_bot_messages` policy).

## Further Reading

- [Multi-Agent Mental Model](../02-mental-models/multi-agent.md)
- [Trust Model](../01-core-concepts/trust-model.md)
- Docs: `docs/multi-agent.md`
