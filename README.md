# skills

Public [Agent Skills](https://agentskills.io) for Claude, packaged as a Claude plugin marketplace. Each skill is its own plugin, so you can install only the ones you want.

## Install

**Claude desktop app** (also makes the skills available on web and mobile): Customize → Personal plugins → **+** → Add marketplace → `rubenspg/skills`, then install the plugins you want.

**Claude Code:**

```
/plugin marketplace add rubenspg/skills
/plugin install wrap-up@skills
```

Update later with `/plugin marketplace update skills`.

## Plugins

| Plugin | What it does |
|---|---|
| `wrap-up` | Closes out a coding or debugging session by filing what was learned where it belongs: a regression test, the commit body, a CLAUDE.md rule, a runbook, or a decision record. |

## Layout

```
.claude-plugin/marketplace.json     catalog of plugins
plugins/<name>/.claude-plugin/plugin.json
plugins/<name>/skills/<name>/SKILL.md
scripts/publish.py                  copies skills in from a private skills repo
```

## Publishing (for the maintainer)

Skills are written in a private repo (`~/.claude/skills`) and published here selectively. List the skills to publish in `~/.claude/skills/public.txt`, then:

```
scripts/publish.py --dry-run   # see what would change
scripts/publish.py --push      # copy, bump versions, commit, push
```

The script refuses to publish a skill containing home paths, private IPs, keys, or credential-looking values (and runs `gitleaks` if installed). Versions bump automatically when a skill's content changes, so installed copies see the update.

## License

MIT. See [LICENSE](LICENSE).
