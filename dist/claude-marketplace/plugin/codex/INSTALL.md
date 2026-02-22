# Installing TopNotch Social for Codex

Enable the social workflow skills in Codex through native skill discovery.

## Prerequisites

- Git
- Codex CLI

## Installation

1. Clone this repository:

```bash
git clone https://github.com/barteksad/top-notch-europe-mesh-ai.git ~/.codex/topnotch-social
```

2. Link the skills directory into Codex's discovery path:

```bash
mkdir -p ~/.agents/skills
ln -s ~/.codex/topnotch-social/skills ~/.agents/skills/topnotch-social
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\topnotch-social" "$env:USERPROFILE\.codex\topnotch-social\skills"
```

3. Restart Codex so it rescans skills.

## Verify

```bash
ls -la ~/.agents/skills/topnotch-social
```

You should see a symlink (or a junction on Windows) pointing to your `skills` directory.

## Update

```bash
cd ~/.codex/topnotch-social
git pull
```

Skills update immediately through the symlink after restart.

## Uninstall

```bash
rm ~/.agents/skills/topnotch-social
```

Optional cleanup:

```bash
rm -rf ~/.codex/topnotch-social
```
