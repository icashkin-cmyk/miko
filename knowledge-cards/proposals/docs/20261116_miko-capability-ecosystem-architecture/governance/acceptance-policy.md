未驗收提案

# Acceptance Policy

## 1. 每階段必要欄位

每一階段都必須明確記錄：目的、輸入、輸出、前置條件、操作要求、禁止事項、檢查點、Acceptance Criteria、Failure Handling、Recovery、Regression Test、閉環條件、負責角色、證據與保存方式。

## 2. 結果狀態

`PASS`：有實際執行證據且符合 AC。
`FAIL`：實際驗證不符合 AC。
`NOT_RUN`：未執行。
`NOT_READ`：來源未讀取。
`BLOCKED`：受授權、依賴或外部服務阻塞。
`UNKNOWN`：證據不足以判定。
`PASS_WITH_REFINEMENT`：方向可行但不可升格為正式 PASS。

UNKNOWN、NOT_RUN、NOT_READ、BLOCKED 不得改寫成 PASS。

## 3. 三方分離

IMPLEMENTER 不得替代 TESTER；TESTER 不得只接受 IMPLEMENTER 的輸出；INDEPENDENT_AUDITOR 必須重新讀取目標、確認版本與 Commit、重新執行必要測試並保存自己的 stdout、stderr、Exit Code、時間與差異。

## 4. 有限迭代

每輪只能修一個可驗收目標。連續兩輪沒有 AC 改善或達五輪上限就停止，交付最佳候選與失敗分析，不宣稱完成。所有外部寫入、推送、合併、正式採用、刪除與發布均需依 MIKO 正本授權。
