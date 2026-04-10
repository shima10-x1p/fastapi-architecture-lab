#!/usr/bin/env bash
# copilot-post-edit.sh
# GitHub Copilot postToolUse hook — ruff（format + lint）と ty（型チェック）を実行する（bash版）
# Copilot CLI（camelCase フィールド）と VSCode（snake_case フィールド）の両方に対応
set -euo pipefail

INPUT=$(cat)

# フィールド名の正規化（CLI: camelCase / VSCode: snake_case）
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // .toolName // empty')

# Python ファイルの編集・作成ツールのみ対象
case "$TOOL_NAME" in
  edit|create|editFiles|createFile|str_replace_editor|replace_string_in_file|multi_replace_string_in_file|create_file)
    ;;
  *)
    echo '{"continue":true}'
    exit 0
    ;;
esac

# ファイルパスの取得（VSCode: tool_input はオブジェクト / CLI: toolArgs は JSON 文字列）
TOOL_INPUT_JSON=$(echo "$INPUT" | jq -c '.tool_input // (.toolArgs | if type == "string" then fromjson else . end) // {}')

FILE_PATH=$(echo "$TOOL_INPUT_JSON" | jq -r '
  .filePath // .file_path // .path //
  (.files // [] | .[0]) //
  empty
' 2>/dev/null || echo "")

# Python ファイルでなければスキップ
if [[ -z "$FILE_PATH" || "$FILE_PATH" != *.py ]]; then
  echo '{"continue":true}'
  exit 0
fi

if [[ ! -f "$FILE_PATH" ]]; then
  echo '{"continue":true}'
  exit 0
fi

MESSAGES=""
EXIT_CODE=0

# ================================================================
# 1. ruff format — 自動フォーマット
# ================================================================
if command -v uv &>/dev/null; then
  uv run ruff format "$FILE_PATH" 2>&1 || true
elif command -v ruff &>/dev/null; then
  ruff format "$FILE_PATH" 2>&1 || true
fi

# ================================================================
# 2. ruff check --fix — lint + 自動修正
# ================================================================
LINT_EXIT=0
if command -v uv &>/dev/null; then
  LINT_OUT=$(uv run ruff check --fix "$FILE_PATH" 2>&1) || LINT_EXIT=$?
elif command -v ruff &>/dev/null; then
  LINT_OUT=$(ruff check --fix "$FILE_PATH" 2>&1) || LINT_EXIT=$?
else
  LINT_OUT="ruff が見つかりません — lint をスキップ"
fi

if [[ $LINT_EXIT -ne 0 ]]; then
  MESSAGES+="[ruff] ${FILE_PATH} に修正できない lint エラーがあります:\n${LINT_OUT}\n"
  EXIT_CODE=1
fi

# ================================================================
# 3. ty check — 型チェック（beta）
# ================================================================
TY_EXIT=0
TY_AVAILABLE=false

if command -v uv &>/dev/null && uv run ty --version &>/dev/null 2>&1; then
  TY_AVAILABLE=true
  TY_OUT=$(uv run ty check "$FILE_PATH" 2>&1) || TY_EXIT=$?
elif command -v ty &>/dev/null; then
  TY_AVAILABLE=true
  TY_OUT=$(ty check "$FILE_PATH" 2>&1) || TY_EXIT=$?
fi

if [[ "$TY_AVAILABLE" == "true" && $TY_EXIT -ne 0 ]]; then
  MESSAGES+="[ty] ${FILE_PATH} に型エラーがあります:\n${TY_OUT}\n"
  EXIT_CODE=1
fi

# ================================================================
# 出力 — Copilot CLI と VSCode 両対応
# ================================================================
if [[ -n "$MESSAGES" ]]; then
  ESCAPED=$(printf '%s' "$MESSAGES" | jq -Rs .)
  cat <<EOF
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": ${ESCAPED}
  }
}
EOF
else
  echo '{"continue":true}'
fi

exit 0
