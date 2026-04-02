const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

let statusBarDaily;
let refreshTimer;

function parsePercent(str) {
    if (!str) return null;
    const m = str.match(/([\d.]+)%/);
    return m ? parseFloat(m[1]) : null;
}


function getQuotaColor(pct) {
    if (pct === null) return '';
    if (pct >= 50) return '';
    if (pct >= 20) return '';
    return '';
}

function getJsonPath() {
    const config = vscode.workspace.getConfiguration('windsurfQuota');
    let p = config.get('jsonPath', '');
    if (!p) {
        // Try workspace folders first
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders) {
            for (const folder of workspaceFolders) {
                const candidate = path.join(folder.uri.fsPath, 'quota_latest.json');
                if (fs.existsSync(candidate)) return candidate;
            }
        }
        // No path configured and not found in workspace folders
        return '';
    }
    return p;
}

function updateStatusBar() {
    const jsonPath = getJsonPath();

    if (!jsonPath || !fs.existsSync(jsonPath)) {
        statusBarDaily.text = '$(sync-ignored) Windsurf: no data';
        statusBarDaily.tooltip = 'quota_latest.json not found. Run windsurf_quota.py first.\nConfigure path in settings: windsurfQuota.jsonPath';
        statusBarDaily.show();
        return;
    }

    try {
        const raw = fs.readFileSync(jsonPath, 'utf8');
        const data = JSON.parse(raw);

        const dailyPct = parsePercent(data.daily_quota);
        const ts = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '?';

        // Daily quota item
        let dailyIcon, dailyColor;
        if (dailyPct === null) {
            dailyIcon = '$(question)';
            dailyColor = new vscode.ThemeColor('statusBar.foreground');
        } else if (dailyPct >= 50) {
            dailyIcon = '$(check)';
            dailyColor = new vscode.ThemeColor('terminal.ansiGreen');
        } else if (dailyPct >= 20) {
            dailyIcon = '$(warning)';
            dailyColor = new vscode.ThemeColor('terminal.ansiYellow');
        } else {
            dailyIcon = '$(error)';
            dailyColor = new vscode.ThemeColor('terminal.ansiRed');
        }

        statusBarDaily.text = `${dailyIcon} ${dailyPct !== null ? dailyPct + '%' : '?'} daily`;
        statusBarDaily.tooltip = `Windsurf Daily Quota: ${data.daily_quota || 'unknown'}\nWeekly Quota: ${data.weekly_quota || 'unknown'}\nUpdated: ${ts}\nClick to refresh`;
        statusBarDaily.color = undefined;
        statusBarDaily.show();

    } catch (e) {
        statusBarDaily.text = '$(error) Windsurf: error';
        statusBarDaily.tooltip = `Failed to read quota_latest.json: ${e.message}`;
    }
}

function activate(context) {
    statusBarDaily = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarDaily.command = 'windsurfQuota.refresh';
    statusBarDaily.text = '$(sync~spin) Windsurf...';
    statusBarDaily.show();
    context.subscriptions.push(statusBarDaily);

    context.subscriptions.push(
        vscode.commands.registerCommand('windsurfQuota.refresh', () => {
            const cfg = vscode.workspace.getConfiguration('windsurfQuota');
            const scriptPath = cfg.get('scriptPath', '');
            const pythonPath = cfg.get('pythonPath', 'python');

            if (!scriptPath) {
                vscode.window.showErrorMessage('Windsurf Quota: set windsurfQuota.scriptPath in settings (path to windsurf_quota.py)');
                return;
            }

            statusBarDaily.text = '$(sync~spin) Syncing...';
            vscode.window.setStatusBarMessage('$(sync~spin) Windsurf: syncing...', 60000);

            // Spawn the quota script — pythonw/python runs silently
            const proc = spawn(pythonPath, [scriptPath], {
                cwd: path.dirname(scriptPath),
                detached: false
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    vscode.window.setStatusBarMessage('$(check) Windsurf quota synced', 3000);
                } else {
                    vscode.window.setStatusBarMessage('$(error) Windsurf sync failed', 4000);
                }
                updateStatusBar();
            });

            proc.on('error', (err) => {
                vscode.window.setStatusBarMessage(`$(error) Windsurf sync error: ${err.message}`, 4000);
                updateStatusBar();
            });
        })
    );

    // Watch the JSON file for changes
    const jsonPath = getJsonPath();
    if (jsonPath) {
        const watcher = fs.watch(path.dirname(jsonPath), (event, filename) => {
            if (filename && filename.includes('quota_latest')) {
                setTimeout(updateStatusBar, 300);
            }
        });
        context.subscriptions.push({ dispose: () => watcher.close() });
    }

    // Also watch on config changes (in case user sets path after activation)
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('windsurfQuota')) {
                updateStatusBar();
            }
        })
    );

    // Periodic refresh
    const config = vscode.workspace.getConfiguration('windsurfQuota');
    const interval = (config.get('refreshIntervalSeconds', 60)) * 1000;
    refreshTimer = setInterval(updateStatusBar, interval);
    context.subscriptions.push({ dispose: () => clearInterval(refreshTimer) });

    updateStatusBar();
}

function deactivate() {
    if (refreshTimer) clearInterval(refreshTimer);
}

module.exports = { activate, deactivate };
