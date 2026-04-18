---
name: "Implement Plan"
description: "作成済みの実装計画をもとに、コード実装 → 単体テスト（Python Test Agent）→ README 更新を一連で実行する"
argument-hint: "実装するプランの概要（省略時は会話履歴・セッションメモリのプランを参照）"
agent: "agent"
---

# 実装計画の実行

渡された引数、または会話履歴・セッションメモリに保存されている最新のプランをもとに、
以下のステップを順に実行する。

---

## Step 1: プランの確認

実行するプランを特定して内容を提示し、ユーザーに確認を取ってから実装を開始する。

プランが複数存在する場合・内容が曖昧な場合は、どのプランを使うかを確認する。

---

## Step 2: コード実装

[copilot-instructions.md](../copilot-instructions.md) の「実装順序」に従って実装を進める。

```
1. domain/        — Entity / Value Object を定義
2. ports/outbound/ — 抽象インターフェースを定義
3. usecases/      — ユースケースを実装（port を引数で受け取る）
4. adapters/outbound/ — 実装（in-memory 実装から始める）
5. adapters/inbound/  — router を追加
```

実装完了後、変更・作成したファイルの一覧を提示する。

---

## Step 3: 単体テスト作成（Python Test Agent）

実装が完了したら、**`Python Test Agent` をサブエージェントとして呼び出して**単体テストを作成する。

サブエージェントへ渡す情報:
- 実装したファイルの一覧（絶対パスまたはリポジトリ相対パス）
- 各ファイルの役割と期待する振る舞い
- テスト観点のヒント（正常系 / 境界値 / 異常系）

> テストの配置は `tests/unit/` 配下で `src/` と同じ階層構造を維持すること。

サブエージェントがテストコードを生成したら、作成されたテストコードについてレビューを行う。
必要に応じて、**`Python Test Agent` をサブエージェントとして呼び出して**テストコードの修正を依頼する。

---

## Step 4: tests/unit/README.md 更新

テスト作成完了後、`.github/skills/test-readme/SKILL.md` のルールに従って
`tests/unit/README.md`（トップレベルおよび該当ディレクトリのサブ README）を更新する。
