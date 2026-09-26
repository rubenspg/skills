#!/usr/bin/env python3
"""Publish skills from your private skills repo into this marketplace.

Reads the skill names listed in ~/.claude/skills/public.txt (one per line,
# for comments), copies each skill into plugins/<name>/skills/<name>/,
writes its plugin.json, bumps the version when content changed, and
regenerates .claude-plugin/marketplace.json.

It never pushes unless you pass --push, and it refuses to publish a skill
that looks like it contains private details unless you pass --force.

Environment overrides: SKILLS_SRC (default ~/.claude/skills),
PUBLIC_LIST (default $SKILLS_SRC/public.txt).
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = Path(os.environ.get("SKILLS_SRC", Path.home() / ".claude" / "skills"))
LIST = Path(os.environ.get("PUBLIC_LIST", SRC / "public.txt"))
STATE = REPO / ".publish-state.json"
MARKET = REPO / ".claude-plugin" / "marketplace.json"
IGNORE = {".git", ".DS_Store", "__pycache__", "node_modules", ".env"}

# Patterns that suggest a skill is not safe to publish.
RISKY = [
    (r"/Users/[A-Za-z0-9._-]+", "absolute macOS home path"),
    (r"\b192\.168\.\d{1,3}\.\d{1,3}\b", "private IP address"),
    (r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "private IP address"),
    (r"\b172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b", "private IP address"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}", "credential-looking value"),
    (r"\bid_ed25519\w*|\bid_rsa\w*", "SSH key reference"),
]


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def read_list():
    if not LIST.exists():
        die(f"{LIST} not found. Create it with one skill name per line.")
    names = []
    for line in LIST.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.append(line)
    return names


def frontmatter(skill_md: Path):
    text = skill_md.read_text()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        die(f"{skill_md} has no YAML frontmatter")
    fields, key, buf = {}, None, []
    for raw in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z_-]+):\s*(.*)$", raw)
        if top and not raw.startswith((" ", "\t")):
            if key:
                fields[key] = " ".join(buf).strip()
            key, val = top.group(1), top.group(2).strip()
            buf = [] if val in (">", ">-", "|", "|-", "") else [val.strip("'\"")]
        elif key:
            buf.append(raw.strip())
    if key:
        fields[key] = " ".join(buf).strip()
    return fields


def short(desc, limit=200):
    first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0]
    return first if len(first) <= limit else first[: limit - 1].rstrip() + "…"


def files_of(folder: Path):
    for p in sorted(folder.rglob("*")):
        if p.is_file() and not (set(p.relative_to(folder).parts) & IGNORE):
            yield p


def digest(folder: Path):
    h = hashlib.sha256()
    for p in files_of(folder):
        h.update(str(p.relative_to(folder)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def scan(folder: Path):
    hits = []
    for p in files_of(folder):
        try:
            text = p.read_text()
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for pat, why in RISKY:
                if re.search(pat, line):
                    hits.append(f"  {p.relative_to(folder)}:{n}  {why}")
    if shutil.which("gitleaks"):
        r = subprocess.run(["gitleaks", "detect", "--no-git", "--redact", "--no-banner",
                            "--source", str(folder)], capture_output=True, text=True)
        if r.returncode != 0:
            hits.append("  gitleaks reported findings:\n" + r.stdout + r.stderr)
    return hits


def bump(version):
    major, minor, patch = (int(x) for x in version.split("."))
    return f"{major}.{minor}.{patch + 1}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="publish even if the privacy scan finds something")
    ap.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    ap.add_argument("--push", action="store_true", help="commit and push when done")
    args = ap.parse_args()

    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    names = read_list()
    changed = []

    for name in names:
        src = SRC / name
        if not (src / "SKILL.md").exists():
            die(f"{src}/SKILL.md not found")
        fm = frontmatter(src / "SKILL.md")
        if fm.get("name") != name:
            die(f"{name}: frontmatter name is '{fm.get('name')}', expected '{name}'")
        if not fm.get("description"):
            die(f"{name}: SKILL.md needs a description")

        hits = scan(src)
        if hits and not args.force:
            print(f"refusing to publish '{name}', it may contain private details:")
            print("\n".join(hits))
            print("fix the skill, or rerun with --force if these are false positives.")
            sys.exit(2)

        h = digest(src)
        prev = state.get(name, {})
        if prev.get("hash") == h:
            print(f"= {name} unchanged ({prev.get('version')})")
            continue
        version = bump(prev["version"]) if prev.get("version") else "0.1.0"
        print(f"+ {name} -> {version}")
        changed.append(name)
        if args.dry_run:
            continue

        dest = REPO / "plugins" / name
        if dest.exists():
            shutil.rmtree(dest)
        (dest / ".claude-plugin").mkdir(parents=True)
        for p in files_of(src):
            out = dest / "skills" / name / p.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)
        (dest / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "name": name,
            "description": short(fm["description"]),
            "version": version,
            "author": {"name": "Rubens"},
        }, indent=2) + "\n")
        state[name] = {"hash": h, "version": version}

    unlisted = sorted(p.name for p in (REPO / "plugins").iterdir()
                      if p.is_dir() and p.name not in names)
    if unlisted:
        print("note: still published but not in public.txt: " + ", ".join(unlisted))
        print("      delete plugins/<name> by hand to unpublish.")

    if args.dry_run:
        return

    market = json.loads(MARKET.read_text())
    entries = []
    for pdir in sorted((REPO / "plugins").iterdir()):
        pj = pdir / ".claude-plugin" / "plugin.json"
        if pj.exists():
            meta = json.loads(pj.read_text())
            entries.append({"name": meta["name"], "source": f"./plugins/{pdir.name}",
                            "description": meta["description"], "version": meta["version"]})
    if changed:
        market["metadata"]["version"] = bump(market["metadata"]["version"])
    market["plugins"] = entries
    MARKET.write_text(json.dumps(market, indent=2) + "\n")
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")

    if args.push and changed:
        msg = "Publish " + ", ".join(changed)
        subprocess.run(["git", "-C", str(REPO), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(REPO), "commit", "-m", msg], check=True)
        subprocess.run(["git", "-C", str(REPO), "push"], check=True)
    elif changed:
        print("review with `git diff`, then commit and push, or rerun with --push.")


if __name__ == "__main__":
    main()
