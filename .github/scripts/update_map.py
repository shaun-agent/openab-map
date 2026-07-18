"""
Agent that reads a diff from openab/beta and updates the mental map.

Called by the sync.yml workflow. Reads diffs from /tmp/, writes updated
markdown files back to the working directory.
"""

import os
import json
import glob
import anthropic

MAP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECTION_FILES = {
    "acp": "01-core-concepts/acp.md",
    "adapters": "01-core-concepts/adapters.md",
    "sessions": "01-core-concepts/sessions.md",
    "directives": "01-core-concepts/directives.md",
    "hooks": "01-core-concepts/hooks.md",
    "trust": "01-core-concepts/trust-model.md",
    "dispatch": "01-core-concepts/dispatch-modes.md",
    "data-flow": "02-mental-models/data-flow.md",
    "topology": "02-mental-models/deployment-topology.md",
    "lifecycle": "02-mental-models/session-lifecycle.md",
    "multi-agent": "02-mental-models/multi-agent.md",
    "deploy-single": "03-use-cases/deploy-single-agent.md",
    "deploy-multi": "03-use-cases/deploy-multi-agent.md",
    "hooks-usecase": "03-use-cases/hook-into-lifecycle.md",
    "cron": "03-use-cases/schedule-agent-tasks.md",
    "which-agent": "04-decision-trees/which-agent.md",
    "which-adapter": "04-decision-trees/which-adapter.md",
    "dispatch-picker": "04-decision-trees/dispatch-mode-picker.md",
    "secrets": "04-decision-trees/secrets-strategy.md",
}


def read_file(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def load_diff_context() -> dict:
    commits = read_file("/tmp/commits.txt")
    diff_stat = read_file("/tmp/diff_stat.txt")
    diff_content = read_file("/tmp/diff_content.txt")
    return {
        "commits": commits,
        "diff_stat": diff_stat,
        "diff_content": diff_content,
        "last_sha": os.environ.get("LAST_SHA", "unknown"),
        "current_sha": os.environ.get("CURRENT_SHA", "unknown"),
    }


def load_current_map() -> dict:
    current = {}
    for key, rel_path in SECTION_FILES.items():
        abs_path = os.path.join(MAP_ROOT, rel_path)
        current[key] = read_file(abs_path)
    return current


def build_system_prompt() -> str:
    return """You are the agent that maintains the OpenAB mental map — a human understanding layer for the openab OSS project.

The mental map is a GitHub repo of structured markdown files that explain OpenAB to deployers and contributors.
Each file covers a specific concept, mental model, use case, or decision tree.

Your job: given a diff from openab/beta, identify which map sections are affected and update them to reflect the changes.

Rules:
- Only update sections that are genuinely affected by the diff. Don't touch unrelated sections.
- Keep the same structure and tone as the existing content.
- Use Mermaid diagrams where they exist — update them if the underlying model changed.
- Write for the reader, not for the diff. The map should still read as documentation, not a changelog.
- The LATEST.md change digest is always updated — it's a plain-English summary of what changed.
- If a change is purely CI/infra (GitHub Actions, Dockerfiles unrelated to config) and has no user-facing impact, note it in LATEST.md but don't update concept files.
- If a change adds a new config option, command, or behavior: update the relevant concept file AND the decision tree if applicable.

Output a JSON object with this shape:
{
  "affected_sections": ["key1", "key2"],   // section keys from the map
  "updates": {
    "key1": "full new content for this file",
    "key2": "full new content for this file"
  },
  "digest": "full new content for 05-change-digest/LATEST.md",
  "reasoning": "brief explanation of what changed and why these sections needed updating"
}

Valid section keys: """ + ", ".join(SECTION_FILES.keys())


def build_user_prompt(diff_ctx: dict, current_map: dict) -> str:
    sections_text = "\n\n".join(
        f"=== {key} ({SECTION_FILES[key]}) ===\n{content}"
        for key, content in current_map.items()
        if content
    )

    return f"""Here is the diff from openab/beta:

COMMITS ({diff_ctx['last_sha']} → {diff_ctx['current_sha']}):
{diff_ctx['commits']}

FILE CHANGES SUMMARY:
{diff_ctx['diff_stat']}

DIFF CONTENT (first 100KB):
{diff_ctx['diff_content']}

---

Here is the current state of all map sections:

{sections_text}

---

Analyze the diff and update the map. Return JSON as specified."""


def run_agent(diff_ctx: dict, current_map: dict) -> dict:
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=build_system_prompt(),
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(diff_ctx, current_map),
            }
        ],
    )

    raw = response.content[0].text

    # Extract JSON — agent may wrap in markdown code block
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    return json.loads(raw)


def apply_updates(result: dict) -> None:
    print(f"Reasoning: {result.get('reasoning', 'none')}")
    print(f"Affected sections: {result.get('affected_sections', [])}")

    for key, new_content in result.get("updates", {}).items():
        if key not in SECTION_FILES:
            print(f"WARNING: unknown section key '{key}', skipping")
            continue
        abs_path = os.path.join(MAP_ROOT, SECTION_FILES[key])
        write_file(abs_path, new_content)
        print(f"Updated: {SECTION_FILES[key]}")

    digest = result.get("digest")
    if digest:
        digest_path = os.path.join(MAP_ROOT, "05-change-digest", "LATEST.md")
        write_file(digest_path, digest)
        print("Updated: 05-change-digest/LATEST.md")


def main() -> None:
    print("Loading diff context...")
    diff_ctx = load_diff_context()

    if not diff_ctx["commits"].strip():
        print("No commits found in diff context. Nothing to do.")
        return

    print("Loading current map...")
    current_map = load_current_map()

    print("Running update agent...")
    result = run_agent(diff_ctx, current_map)

    print("Applying updates...")
    apply_updates(result)

    print("Done.")


if __name__ == "__main__":
    main()
