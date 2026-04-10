# copilot-session-start.ps1
# GitHub Copilot sessionStart hook — uv / ruff / ty の存在確認（PowerShell版）
$ErrorActionPreference = "Continue"

[Console]::In.ReadToEnd() | Out-Null
$contextParts = @()

# Python バージョン
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pyCmd) {
    $pyVer = & python --version 2>&1
    $contextParts += "Python: $pyVer"
}

# uv
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if ($uvCmd) {
    $uvVer = & uv --version 2>&1
    $contextParts += "uv: $uvVer [OK]"
} else {
    $contextParts += "uv: 未インストール — Install: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`""
}

# ruff
$ruffAvailable = $false
if ($uvCmd) {
    & uv run ruff --version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $ruffVer = & uv run ruff --version 2>&1
        $contextParts += "ruff: $ruffVer [OK]"
        $ruffAvailable = $true
    }
}
if (-not $ruffAvailable) {
    $ruffCmd = Get-Command ruff -ErrorAction SilentlyContinue
    if ($ruffCmd) {
        $ruffVer = & ruff --version 2>&1
        $contextParts += "ruff: $ruffVer [OK]"
        $ruffAvailable = $true
    } else {
        $contextParts += "ruff: 未インストール — Install: uv add --dev ruff"
        # 自動インストール試行
        if ($uvCmd) {
            & uv add --dev ruff 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $contextParts[-1] = "ruff: uv 経由でインストール完了 [OK]"
            }
        }
    }
}

# ty（beta）
$tyAvailable = $false
if ($uvCmd) {
    & uv run ty --version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $tyVer = & uv run ty --version 2>&1
        $contextParts += "ty: $tyVer [OK] (beta)"
        $tyAvailable = $true
    }
}
if (-not $tyAvailable) {
    $tyCmd = Get-Command ty -ErrorAction SilentlyContinue
    if ($tyCmd) {
        $tyVer = & ty --version 2>&1
        $contextParts += "ty: $tyVer [OK] (beta)"
    } else {
        $contextParts += "ty: 未インストール (beta) — Install: uv add --dev ty"
    }
}

# pyproject.toml の存在確認
if (Test-Path "pyproject.toml") {
    $contextParts += "pyproject.toml: 存在確認 [OK]"
} else {
    $contextParts += "pyproject.toml: 見つかりません — uv init を実行してください"
}

$contextString = $contextParts -join "`n"

$output = @{
    "hookSpecificOutput" = @{
        "hookEventName"    = "SessionStart"
        "additionalContext" = $contextString
    }
}
$output | ConvertTo-Json -Compress -Depth 5

exit 0
