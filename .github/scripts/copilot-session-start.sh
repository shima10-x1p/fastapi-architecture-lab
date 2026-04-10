#!/usr/bin/env bash
# copilot-session-start.sh
# GitHub Copilot sessionStart hook — uv / ruff / ty の存在確認（bash版）
set -euo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // "."')

CONTEXT_PARTS=()

# Python バージョン
if command -v python &>/dev/null; then
  PY_VER=$(python --version 2>&1)
  CONTEXT_PARTS+=("Python: $PY_VER")
fi

# uv
if command -v uv &>/dev/null; then
  UV_VER=$(uv --version 2>&1)
  CONTEXT_PARTS+=("uv: $UV_VER [OK]")
else
  CONTEXT_PARTS+=("uv: 未インストール — Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
fi

# ruff
RUFF_FOUND=false
if command -v uv &>/dev/null && uv run ruff --version &>/dev/null 2>&1; then
  RUFF_VER=$(uv run ruff --version 2>&1)
  CONTEXT_PARTS+=("ruff: $RUFF_VER [OK]")
  RUFF_FOUND=true
elif command -v ruff &>/dev/null; then
  RUFF_VER=$(ruff --version 2>&1)
  CONTEXT_PARTS+=("ruff: $RUFF_VER [OK]")
  RUFF_FOUND=true
fi

if [[ "$RUFF_FOUND" == "false" ]]; then
  CONTEXT_PARTS+=("ruff: 未インストール — Install: uv add --dev ruff")
  # 自動インストール試行
  if command -v uv &>/dev/null; then
    uv add --dev ruff 2>/dev/null && CONTEXT_PARTS[-1]="ruff: uv 経由でインストール完了 [OK]" || true
  fi
fi

# ty（beta）
if command -v uv &>/dev/null && uv run ty --version &>/dev/null 2>&1; then
  TY_VER=$(uv run ty --version 2>&1)
  CONTEXT_PARTS+=("ty: $TY_VER [OK] (beta)")
elif command -v ty &>/dev/null; then
  TY_VER=$(ty --version 2>&1)
  CONTEXT_PARTS+=("ty: $TY_VER [OK] (beta)")
else
  CONTEXT_PARTS+=("ty: 未インストール (beta) — Install: uv add --dev ty")
fi

# pyproject.toml の存在確認
if [[ -f "$CWD/pyproject.toml" ]]; then
  CONTEXT_PARTS+=("pyproject.toml: 存在確認 [OK]")
else
  CONTEXT_PARTS+=("pyproject.toml: 見つかりません — uv init を実行してください")
fi

CONTEXT_STRING=$(printf '%s\n' "${CONTEXT_PARTS[@]}" | jq -Rs .)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": ${CONTEXT_STRING}
  }
}
EOF

exit 0
