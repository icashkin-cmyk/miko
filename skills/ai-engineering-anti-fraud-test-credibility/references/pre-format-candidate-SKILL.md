---
name: ai-engineering-anti-fraud-test-credibility
description: AI 工程測試反造假、測試有效性與驗收證據可信度檢查時使用：要求完整執行證據、正負向與邊界測試、異常測試、回歸測試、Mutation Testing、錯誤注入與狀態誠實標記；禁止以 AI 自述或預期輸出冒充 PASS。
---
# AI 工程反造假與測試可信度規範 v1.1-candidate

> 來源附約：`/home/ubuntu/upload/pasted_content.txt` 第六節；文件狀態 `PROPOSED`；採用狀態 `PENDING`。角色分離與模式選擇由 `three-party-review` 負責，本 Skill 不重複定義角色責任。

## 1. 強制測試證據欄位

每項必要測試至少保存：

| 欄位 | 要求 |
|---|---|
| `TEST_ID` | 唯一測試識別碼 |
| `TARGET` | 實際測試對象與路徑 |
| `VERSION` | 版本、Branch、Commit |
| `HASH` | 交付物完整性 |
| `ENVIRONMENT` | 執行環境 |
| `COMMAND` | 實際執行命令 |
| `STDOUT` | 實際標準輸出；不得填預期輸出 |
| `STDERR` | 實際錯誤輸出 |
| `EXIT_CODE` | 實際程序結束碼 |
| `RESULT` | `PASS`／`FAIL`／`NOT_RUN`／`BLOCKED`／`NOT_READ`／`UNKNOWN` |
| `EVIDENCE` | 可追溯證據路徑 |

沒有實際執行就填 `NOT_RUN`；不存在證據時不得填 `PASS`。

## 2. 測試有效性

依工作風險選擇並實際執行：

- 正向測試。
- 負向測試。
- 邊界測試。
- 異常測試。
- Regression Testing。
- Mutation Testing。
- 錯誤注入。

測試必須證明能識別預期錯誤。Mutation 未被抓到時，測試有效性為 `FAIL`，不得將部分通過視為整體合格。

## 3. 反造假禁止事項

禁止未執行卻宣稱通過、以預期輸出冒充實際輸出、隱藏失敗、把 SKIP／NOT_RUN／UNKNOWN 當 PASS、只測正常路徑、把本機結果冒充遠端結果、把文件完整冒充 Runtime 已啟用。

## 4. 結果與放行

`UNKNOWN`、`NOT_RUN`、`BLOCKED` 不得轉換成 `PASS`。每項必要 AC 都必須有實際證據；測試者與獨立驗收者的證據分開保存。正式採用仍須由 `three-party-review` 的 `INDEPENDENTLY_AUDITED` 模式處理。

## 5. 反向測試

建立來源原子項目與候選輸出的雙向 coverage matrix；檢查來源遺失、輸出無來源、責任越界、否定條款遺失、例外遺失、失敗出口遺失、狀態升格與證據欄位缺失。以 mutation 改壞一個原子項目，反向測試必須報告失敗。
