# copilot-post-edit.ps1
# GitHub Copilot postToolUse hook — ruff（format + lint）と ty（型チェック）を実行する（PowerShell版）
# Copilot CLI（camelCase フィールド）と VSCode（snake_case フィールド）の両方に対応
$ErrorActionPreference = "Continue"

$inputJson = [Console]::In.ReadToEnd()
$inputObj = $inputJson | ConvertFrom-Json

# フィールド名の正規化（CLI: camelCase / VSCode: snake_case）
$toolName = if ($inputObj.tool_name) { $inputObj.tool_name }
            elseif ($inputObj.toolName) { $inputObj.toolName }
            else { "" }

# Python ファイルの編集・作成ツールのみ対象
$editTools = @(
    "edit", "create",
    "editFiles", "createFile",
    "str_replace_editor",
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "create_file"
)
if ($toolName -notin $editTools) {
    Write-Output '{"continue":true}'
    exit 0
}

# ファイルパスの取得（VSCode: tool_input はオブジェクト / CLI: toolArgs は JSON 文字列）
$toolInput = if ($inputObj.tool_input) { $inputObj.tool_input }
             elseif ($inputObj.toolArgs) {
                 if ($inputObj.toolArgs -is [string]) {
                     $inputObj.toolArgs | ConvertFrom-Json
                 } else { $inputObj.toolArgs }
             } else { @{} }

$filePath = if ($toolInput.filePath) { $toolInput.filePath }
            elseif ($toolInput.file_path) { $toolInput.file_path }
            elseif ($toolInput.path) { $toolInput.path }
            elseif ($toolInput.files -and $toolInput.files.Count -gt 0) { $toolInput.files[0] }
            else { "" }

# Python ファイルでなければスキップ
if ([string]::IsNullOrEmpty($filePath) -or -not $filePath.EndsWith(".py")) {
    Write-Output '{"continue":true}'
    exit 0
}

if (-not (Test-Path $filePath)) {
    Write-Output '{"continue":true}'
    exit 0
}

$messages = @()
$hasErrors = $false

$hasUv   = $null -ne (Get-Command uv   -ErrorAction SilentlyContinue)
$hasRuff = $null -ne (Get-Command ruff -ErrorAction SilentlyContinue)
$hasTy   = $null -ne (Get-Command ty   -ErrorAction SilentlyContinue)

# ================================================================
# 1. ruff format — 自動フォーマット
# ================================================================
if ($hasUv) {
    & uv run ruff format $filePath 2>&1 | Out-Null
} elseif ($hasRuff) {
    & ruff format $filePath 2>&1 | Out-Null
}

# ================================================================
# 2. ruff check --fix — lint + 自動修正
# ================================================================
if ($hasUv) {
    $lintOut  = & uv run ruff check --fix $filePath 2>&1
    $lintExit = $LASTEXITCODE
} elseif ($hasRuff) {
    $lintOut  = & ruff check --fix $filePath 2>&1
    $lintExit = $LASTEXITCODE
} else {
    $lintOut  = "ruff が見つかりません — lint をスキップ"
    $lintExit = 0
}

if ($lintExit -ne 0) {
    $messages  += "[ruff] ${filePath} に修正できない lint エラーがあります:`n$($lintOut -join "`n")"
    $hasErrors  = $true
}

# ================================================================
# 3. ty check — 型チェック（beta）
# ================================================================
$tyAvailable = $false
if ($hasUv) {
    & uv run ty --version 2>&1 | Out-Null
    $tyAvailable = ($LASTEXITCODE -eq 0)
}
if (-not $tyAvailable) { $tyAvailable = $hasTy }

if ($tyAvailable) {
    if ($hasUv) {
        $tyOut  = & uv run ty check $filePath 2>&1
        $tyExit = $LASTEXITCODE
    } else {
        $tyOut  = & ty check $filePath 2>&1
        $tyExit = $LASTEXITCODE
    }

    if ($tyExit -ne 0) {
        $messages  += "[ty] ${filePath} に型エラーがあります:`n$($tyOut -join "`n")"
        $hasErrors  = $true
    }
}

# ================================================================
# 出力 — Copilot CLI と VSCode 両対応
# ================================================================
if ($hasErrors) {
    $combinedMessage = $messages -join "`n`n"
    $output = @{
        "continue"           = $true
        "hookSpecificOutput" = @{
            "hookEventName"   = "PostToolUse"
            "additionalContext" = $combinedMessage
        }
    }
    $output | ConvertTo-Json -Compress -Depth 5
} else {
    Write-Output '{"continue":true}'
}

exit 0
