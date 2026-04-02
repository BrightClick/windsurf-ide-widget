# Windsurf Quota Status Bar

Shows your Windsurf **daily quota %** and **extra balance $** in the VS Code / Windsurf IDE status bar.

## Status Bar Items

```
✓ 71.00% daily    💳 $94.03
```

- Click the **%** item to refresh immediately
- Click the **$** item to open the dashboard at http://127.0.0.1:8050

## Installation

### Option A: Install from folder (easiest)

1. Copy the `windsurf-quota` folder to your extensions directory:
   ```
   %USERPROFILE%\.vscode\extensions\windsurf-quota
   ```
   or for Windsurf:
   ```
   %USERPROFILE%\.windsurf\extensions\windsurf-quota
   ```
2. Restart VS Code / Windsurf

### Option B: Install with vsce (for packaging)

```bash
npm install -g @vscode/vsce
cd windsurf-quota
vsce package
code --install-extension windsurf-quota-1.0.0.vsix
```

## Configuration

In VS Code settings (`Ctrl+,`), search for **Windsurf Quota**:

| Setting | Default | Description |
|---|---|---|
| `windsurfQuota.jsonPath` | auto-detect | Full path to `quota_latest.json` |
| `windsurfQuota.refreshIntervalSeconds` | `60` | How often to re-read the file |

The extension will auto-detect `quota_latest.json` if it's in your open workspace folder.

## How it works

1. `windsurf_quota.py` scrapes Windsurf and writes `quota_latest.json`
2. The extension reads that file and shows the values in the status bar
3. The file watcher detects changes instantly when you re-run the scraper
