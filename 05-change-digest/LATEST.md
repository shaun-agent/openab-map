# Latest Change Digest

> Auto-generated. Last updated from openab `beta` branch.
> Source SHA: see [`.sync-state`](../.sync-state)

---

## Recent Changes in openab/beta

### fix(claude): ACP default command, version bumps, auth docs, CI coverage
**Commit:** `2e3292b`

- Updated ACP default command for the Claude Code adapter
- Version bumps across several crates
- Auth documentation improvements
- Expanded CI test coverage

**Map sections affected:** [Which Agent?](../04-decision-trees/which-agent.md) — claude-agent-acp command syntax may have changed. Verify against latest `docs/platforms/` in source.

---

### ci(issues): close unlinked stale issues instead of report-only
**Commit:** `30bc145`

Infrastructure change to CI workflow. No impact on user-facing behavior or map content.

---

### ci(pr-review): add /review comment command for targeted PR review
**Commit:** `a36b1ef`

Contributor workflow improvement. Added `/review` comment trigger for targeted PR review via GitHub Actions.

**Relevant for:** contributors — you can now trigger focused review on a PR by commenting `/review`.

---

## No Breaking Changes in This Window

All recent commits are fixes and CI improvements. No config schema changes, no new required fields, no renamed commands.

---

*Next update: triggered by next push to openab/beta or daily schedule.*
