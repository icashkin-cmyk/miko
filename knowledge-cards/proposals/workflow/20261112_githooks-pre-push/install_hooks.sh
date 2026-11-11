#!/usr/bin/env bash
# 安裝 pre-push 到指定的 miko repo（提案）。
# 和手冊〈安裝方式〉的差別：
#  1. 手冊先 chmod、沒有建檔步驟，空資料夾照抄 chmod 失敗（2026-11-10 實跑 rc=1）→ 本檔先複製再 chmod。
#  2. 手冊把 hook 放 repo 內 .githooks/ 並改 core.hooksPath → miko 是公開 repo，本檔改裝到 .git/hooks/（不進版控、不改設定）。
# 用法：bash install_hooks.sh <miko repo 路徑>
set -euo pipefail
SRC=$(cd "$(dirname "$0")" && pwd)
DST=${1:?用法：bash install_hooks.sh <miko repo 路徑>}
HP=$(git -C "$DST" config core.hooksPath || true)
[ -z "$HP" ] || { echo "這個 repo 設了 core.hooksPath=$HP，本檔不覆蓋設定；請手動處理" >&2; exit 1; }
HD=$(cd "$DST" && cd "$(git rev-parse --git-path hooks)" && pwd)
[ ! -e "$HD/pre-push" ] || cp "$HD/pre-push" "$HD/pre-push.bak.$(date +%Y%m%d%H%M%S)"
cp "$SRC/pre-push" "$HD/pre-push"
chmod +x "$HD/pre-push"
echo "已安裝：$HD/pre-push"
