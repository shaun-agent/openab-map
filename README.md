# OpenAB Mental Map

> A living, agent-maintained understanding layer for [OpenAB](https://github.com/openabdev/openab) — the open Agent Client Protocol broker.

This repo is auto-updated by an agent workflow that watches the `beta` branch of openab, diffs what changed, and rewrites affected sections. Every file traces back to a source commit SHA in `.sync-state`.

**If you're new → start at [What is OpenAB](./00-what-is-openab.md)**

---

## Map Layers

| Layer | What it answers |
|-------|----------------|
| [00 · What is OpenAB](./00-what-is-openab.md) | One-page pitch. The problem, the solution, what it is not. |
| [01 · Core Concepts](./01-core-concepts/) | The 7 ideas you must internalize before anything clicks. |
| [02 · Mental Models](./02-mental-models/) | How the pieces fit — data flows, topology, sequences. |
| [03 · Use Cases](./03-use-cases/) | "I want to do X" → here's how. |
| [04 · Decision Trees](./04-decision-trees/) | Should I use X or Y? Structured branching choices. |
| [05 · Change Digest](./05-change-digest/LATEST.md) | Plain-English summary of recent openab changes. |

---

## How This Repo Stays Current

```
openab/beta push or daily schedule
        ↓
  GitHub Action: compute diff since last sync
        ↓
  Claude agent: reads diff + current map
        ↓
  Rewrites affected sections + updates LATEST.md
        ↓
  Opens PR
        ↓
  Multi-agent review via openab b2b
        ↓
  Auto-merge on consensus
```

The agents doing the review run through openab itself — the same system being documented. See [`.github/workflows/sync.yml`](./.github/workflows/sync.yml).

---

## Tracked Source

- **Repo:** `openabdev/openab`
- **Branch:** `beta`
- **Last synced SHA:** see [`.sync-state`](./.sync-state)

---

## Contributing

This map is agent-maintained but human-correctable. If a section is wrong or missing:

1. Open an issue describing the gap
2. Or open a PR — the next agent sync will reconcile your changes against the source

Priority areas that benefit most from human input: decision trees, use-case narratives, and "gotchas" that aren't visible from the code alone.
