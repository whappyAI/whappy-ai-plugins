# Whappy plugins for Claude Code and Codex

Whappy runs AI setters on WhatsApp and Instagram: they answer your leads, ask your
qualifying questions and book the appointment. This plugin connects Claude Code or
Codex to your Whappy account through the Whappy connector
(`https://mcp.whappy.ai/mcp`) and adds three workflows:

| Skill | What it does |
| --- | --- |
| `build-a-campaign` | From a website or a business description to a built, checked and rehearsed campaign. You launch it in the dashboard. |
| `daily-inbox-review` | Unread chats, chats waiting on a human, chats in error, and what to do with each. |
| `weekly-report` | Leads, conversations, appointments, the funnel, Coach suggestions and next steps for the week. |

Two commands run the last two directly: `/whappy:inbox` and `/whappy:report`.

The plugin holds no secrets and no hooks. It only declares the connector and the
instructions above; you sign in to Whappy in your browser the first time a tool runs.

## Install in Claude Code

In a Claude Code session:

```text
/plugin marketplace add whappyAI/whappy-ai-plugins
/plugin install whappy@whappy-ai-plugins
```

From a shell, the same steps are
`claude plugin marketplace add whappyAI/whappy-ai-plugins` and
`claude plugin install whappy@whappy-ai-plugins`.

Then run `/mcp`, pick `plugin:whappy:whappy` and sign in. The skills appear as
`/whappy:build-a-campaign`, `/whappy:daily-inbox-review` and `/whappy:weekly-report`,
and Claude also uses them on its own when your request matches.

## Install in Codex

```bash
codex plugin marketplace add whappyAI/whappy-ai-plugins
```

Then open the plugin directory in Codex (`/plugins`), choose the **Whappy**
marketplace and install **Whappy**. Codex signs you in to Whappy when you install it.
Without the plugin, the connector alone is
`codex mcp add whappy --url https://mcp.whappy.ai/mcp` followed by
`codex mcp login whappy`.

## Other assistants

Claude on the web, desktop and mobile, ChatGPT and other MCP clients can add the
connector by URL: `https://mcp.whappy.ai/mcp`. See
[Claude and other MCP clients](https://docs.whappy.ai/integrations/mcp). Gemini CLI
has its own extension: [whappyAI/gemini-cli-extension](https://github.com/whappyAI/gemini-cli-extension).

## Permissions

When you connect, Whappy shows a consent page with the client that is asking, the
account you are signed in with and where you will be sent back. You choose
**Allow** or **Deny**; there is no access level to pick.

A connected assistant can:

- build a campaign from a website or a description, and create, rename, duplicate or
  delete campaigns;
- read, generate and edit the funnel, the knowledge and the qualifying questions;
- draft WhatsApp templates, translate them, submit them to Meta and send a test
  template to a phone number you give it;
- change a campaign's working hours, time zone and start delay;
- rehearse a campaign with synthetic leads, who are never messaged;
- read your leads, conversations, results, Coach reports, calendar settings and plan.

It cannot start or stop a campaign, message your leads, add leads, change billing or
your account, or connect WhatsApp or Instagram (it gives you a link to finish in the
browser). The tools that delete a campaign, a knowledge document, a question or a
funnel step are marked destructive, so assistants that honour the mark, such as
Claude and Codex, ask you before calling them. AI generation is limited to 30 requests per
hour per account, shared with the assistant in the dashboard.

Some tools the skills mention are marked "when available": they are planned and not
yet offered by the connector. The skills use them only once the connector lists them.

To disconnect, remove the connector in your client or uninstall the plugin; the
client tells Whappy to revoke the access. There is not yet a dashboard page listing
your connections: if you lost access to the client,
[contact support](https://docs.whappy.ai/support/contact-support) and we revoke it.

## Support and privacy

- Support: [docs.whappy.ai/support/contact-support](https://docs.whappy.ai/support/contact-support)
  or <team@whappy.ai>
- Documentation: [docs.whappy.ai/integrations/mcp](https://docs.whappy.ai/integrations/mcp)
- Privacy policy: [whappy.ai/legal/privacy](https://whappy.ai/legal/privacy)
- Terms: [whappy.ai/legal/terms](https://whappy.ai/legal/terms)

Data you read through the connector goes to the AI vendor of the assistant you
connected, under your own agreement with that vendor.

## MCP Registry

`server.json` lists the connector in the official MCP Registry as `ai.whappy/whappy`
(remote only, Streamable HTTP). The namespace `ai.whappy` is proven by a DNS TXT
record on the apex of `whappy.ai`:

```text
whappy.ai. IN TXT "v=MCPv1; k=ed25519; p=Y3WT2o9ZEA8vhGpj1l+CfWTP7Xxyel7aSaS4+MZBM3A="
```

Add it at the apex (`whappy.ai`, host `@`), not under a subdomain. It can sit next to
other TXT records such as SPF. Check it with `dig TXT whappy.ai +short`.

The matching Ed25519 private key is not in this repository. Store it, as the hex
string that `mcp-publisher login dns --private-key` takes, in the GitHub Actions
secret `MCP_PRIVATE_KEY` on an environment named `mcp-registry-publish`, limited to
`v*` tags and with a required reviewer.
`.github/workflows/publish-mcp-registry.yml` then publishes on every `v*` tag whose
version matches `server.json`.

## Releasing

1. Change the version in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
   and `server.json` together (a test checks that they agree).
2. Merge to `main` with CI green.
3. Tag `vX.Y.Z` and push the tag. The registry workflow publishes `server.json`.
   Claude Code and Codex users get the new version when they update the marketplace.

## Development

```bash
claude plugin validate . --strict          # plugin and marketplace (Claude Code)
python3 -m unittest discover -s tests -v   # URL, manifests, skill tool names, no secrets
npx --yes markdownlint-cli2                # Markdown lint
```

CI (`.github/workflows/ci.yml`) runs these, plus a JSON schema check of the Codex
manifests (`schemas/`) and `mcp-publisher validate server.json`.

`tests/connector_tools.json` is the list of tools the connector exposes, copied from
the Whappy backend's connector profile. A skill may name only a listed tool, and a
planned tool only on a line that says "when available". Update the list when the
connector changes.

## Layout

```text
.claude-plugin/plugin.json        Claude Code plugin manifest
.claude-plugin/marketplace.json   Claude Code marketplace (this repo)
.codex-plugin/plugin.json         Codex plugin manifest
.agents/plugins/marketplace.json  Codex marketplace (this repo)
.mcp.json                         the Whappy connector, shared by both
server.json                       MCP Registry entry
skills/                           the three skills
commands/                         /whappy:inbox and /whappy:report
schemas/                          JSON schemas for the Codex manifests
tests/                            contract tests
```

## Sources

File formats checked against the vendors' documentation on 2026-11-22:

- Claude Code plugin manifest: <https://code.claude.com/docs/en/plugins-reference>
- Claude Code components (skills, commands, `.mcp.json`): <https://code.claude.com/docs/en/plugins/components.md>
- Claude Code marketplaces: <https://code.claude.com/docs/en/plugin-marketplaces> and <https://code.claude.com/docs/en/plugins/marketplace-reference.md>
- Codex plugins and marketplaces: <https://developers.openai.com/plugins/build/plugins.md>
- Codex manifest parser: <https://github.com/openai/codex/blob/cf3ff1530d821ec2d26452da4971d8e3e7d18d25/codex-rs/core-plugins/src/manifest.rs> and `marketplace.rs` in the same directory
- Codex compatibility examples: <https://github.com/openai/plugins/tree/main/plugins/notion>
- MCP Registry, remote servers: <https://modelcontextprotocol.io/registry/remote-servers.md>
- MCP Registry, DNS authentication: <https://modelcontextprotocol.io/registry/authentication.md>
- MCP Registry, GitHub Actions: <https://modelcontextprotocol.io/registry/github-actions.md>
- `server.json` schema: <https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json>

## License

MIT, see [LICENSE](LICENSE).
