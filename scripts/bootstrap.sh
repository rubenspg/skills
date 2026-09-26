#!/usr/bin/env bash
# One-time setup: creates the public GitHub repo "skills" under your account
# and pushes this marketplace to it. Needs the GitHub CLI, logged in.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v gh >/dev/null || { echo "Install the GitHub CLI first: brew install gh"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Run: gh auth login"; exit 1; }

GH_USER="$(gh api user --jq .login)"
if gh repo view "$GH_USER/skills" >/dev/null 2>&1; then
  echo "$GH_USER/skills already exists on GitHub. Stopping so nothing gets overwritten."
  exit 1
fi

perl -pi -e "s/YOUR_GH_USER/$GH_USER/g" README.md

[ -d .git ] || git init -q -b main
git add -A
git commit -q -m "Create skills marketplace with wrap-up plugin"
gh repo create skills --public --source . --remote origin --push \
  --description "Public Agent Skills for Claude, installable as a plugin marketplace"

cat <<MSG

Done: https://github.com/$GH_USER/skills

Claude desktop app: Customize → Personal plugins → + → Add marketplace → $GH_USER/skills
Claude Code:        /plugin marketplace add $GH_USER/skills
                    /plugin install wrap-up@skills
MSG
