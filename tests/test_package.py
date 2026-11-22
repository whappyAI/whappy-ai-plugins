"""Contract tests for the whappy-ai-plugins package.

Standard library only, so CI and a laptop run the same thing:

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_MCP_URL = "https://mcp.whappy.ai/mcp"
REGISTRY_NAME = "ai.whappy/whappy"
PLUGIN_NAME = "whappy"
MARKETPLACE_NAME = "whappy-ai-plugins"
SKILLS = ("build-a-campaign", "daily-inbox-review", "weekly-report")
COMMANDS = {"inbox": "daily-inbox-review", "report": "weekly-report"}

# A backticked token made only of lowercase words joined by underscores is read
# as a tool name, e.g. `campaign_health`. Arguments are written `name=value`.
TOOL_TOKEN = re.compile(r"`([a-z]+(?:_[a-z]+)+)`")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def frontmatter(path: Path) -> dict[str, str]:
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError(f"{path} has no YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


class McpConfigTest(unittest.TestCase):
    def test_mcp_json_points_at_production_resource(self) -> None:
        servers = load_json(".mcp.json")["mcpServers"]
        self.assertEqual(list(servers), ["whappy"])
        self.assertEqual(servers["whappy"], {"type": "http", "url": PRODUCTION_MCP_URL})

    def test_registry_entry_uses_the_same_url(self) -> None:
        server = load_json("server.json")
        self.assertEqual(server["name"], REGISTRY_NAME)
        self.assertEqual(
            server["remotes"], [{"type": "streamable-http", "url": PRODUCTION_MCP_URL}]
        )
        self.assertTrue(
            server["$schema"].startswith("https://static.modelcontextprotocol.io/schemas/")
        )
        self.assertLessEqual(len(server["description"]), 100)

    def test_codex_manifest_uses_the_shared_mcp_json(self) -> None:
        self.assertEqual(load_json(".codex-plugin/plugin.json")["mcpServers"], "./.mcp.json")


class ManifestConsistencyTest(unittest.TestCase):
    def test_plugin_names_agree(self) -> None:
        claude = load_json(".claude-plugin/plugin.json")
        codex = load_json(".codex-plugin/plugin.json")
        claude_market = load_json(".claude-plugin/marketplace.json")
        codex_market = load_json(".agents/plugins/marketplace.json")
        self.assertEqual(claude["name"], PLUGIN_NAME)
        self.assertEqual(codex["name"], PLUGIN_NAME)
        self.assertEqual([p["name"] for p in claude_market["plugins"]], [PLUGIN_NAME])
        self.assertEqual([p["name"] for p in codex_market["plugins"]], [PLUGIN_NAME])
        self.assertEqual(claude_market["name"], MARKETPLACE_NAME)
        self.assertEqual(codex_market["name"], MARKETPLACE_NAME)

    def test_marketplaces_point_at_the_repo_root(self) -> None:
        claude_market = load_json(".claude-plugin/marketplace.json")
        codex_market = load_json(".agents/plugins/marketplace.json")
        self.assertEqual(claude_market["plugins"][0]["source"], "./")
        self.assertEqual(
            codex_market["plugins"][0]["source"], {"source": "local", "path": "./"}
        )

    def test_versions_agree(self) -> None:
        versions = {
            load_json(".claude-plugin/plugin.json")["version"],
            load_json(".codex-plugin/plugin.json")["version"],
            load_json("server.json")["version"],
        }
        self.assertEqual(len(versions), 1, versions)

    def test_no_hooks_anywhere(self) -> None:
        self.assertFalse((ROOT / "hooks").exists())
        for manifest in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            self.assertNotIn("hooks", load_json(manifest))


class SkillTest(unittest.TestCase):
    tools: dict[str, Any] = load_json("tests/connector_tools.json")

    def skill_paths(self) -> list[Path]:
        return sorted((ROOT / "skills").glob("*/SKILL.md"))

    def test_expected_skills_exist(self) -> None:
        self.assertEqual(tuple(p.parent.name for p in self.skill_paths()), SKILLS)

    def test_frontmatter_names_match_directories(self) -> None:
        for path in self.skill_paths():
            fields = frontmatter(path)
            self.assertEqual(fields.get("name"), path.parent.name, path)
            self.assertGreater(len(fields.get("description", "")), 40, path)

    def test_skills_name_only_real_or_planned_tools(self) -> None:
        live = set(self.tools["live"])
        planned = set(self.tools["planned"])
        known = live | planned | set(self.tools["not_tools"])
        self.assertFalse(live & planned, "a tool cannot be both live and planned")
        sources = self.skill_paths() + sorted((ROOT / "commands").glob("*.md"))
        for path in sources:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for token in TOOL_TOKEN.findall(line):
                    where = f"{path.relative_to(ROOT)}:{number}"
                    self.assertIn(token, known, f"{where}: unknown tool `{token}`")
                    if token in planned:
                        self.assertIn(
                            "when available",
                            line.lower(),
                            f"{where}: `{token}` is not live; say 'when available'",
                        )

    def test_the_skill_checker_rejects_an_invented_tool(self) -> None:
        self.assertEqual(TOOL_TOKEN.findall("call `leads_delete_all` now"), ["leads_delete_all"])
        self.assertNotIn("leads_delete_all", self.tools["live"])


class CommandTest(unittest.TestCase):
    def test_commands_point_at_existing_skills(self) -> None:
        for command, skill in COMMANDS.items():
            path = ROOT / "commands" / f"{command}.md"
            self.assertIn(f"`{skill}`", path.read_text(encoding="utf-8"), path)
            self.assertTrue((ROOT / "skills" / skill / "SKILL.md").is_file())
            self.assertIn("description", frontmatter(path))


class SecretsTest(unittest.TestCase):
    FORBIDDEN = (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"\b[0-9a-f]{64}\b"),
        re.compile(r"(?i)client_secret\"\s*:"),
    )

    def test_no_private_key_material_in_the_repo(self) -> None:
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in self.FORBIDDEN:
                self.assertIsNone(pattern.search(text), f"{path}: matches {pattern.pattern}")

    def test_publish_workflow_reads_the_key_from_a_secret(self) -> None:
        workflow = (ROOT / ".github/workflows/publish-mcp-registry.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("secrets.MCP_PRIVATE_KEY", workflow)
        self.assertIn("login dns --domain whappy.ai", workflow)


if __name__ == "__main__":
    unittest.main()
