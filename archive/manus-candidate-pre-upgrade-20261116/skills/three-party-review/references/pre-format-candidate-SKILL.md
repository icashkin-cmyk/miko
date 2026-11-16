---
name: three-party-review
description: 需要製作者、測試者與獨立驗收者分離，或需要在 STAGED_SELF_AUDIT 與 INDEPENDENTLY_AUDITED 之間選擇驗收模式時使用；適用 Skill、治理規則、文件交付、正式採用、PR 合併與版本發布前的責任隔離。
---
# 三方審查 v1.1-candidate

> 來源附約：`/home/ubuntu/upload/pasted_content.txt`；文件狀態 `PROPOSED`；採用狀態 `PENDING`。本 Skill 候選不宣稱附約已成為 MIKO 正式規則。

## 1. 三個正式角色

### IMPLEMENTER｜製作者

理解需求與 AC，製作／修改候選成果，保存來源、版本、Commit、檔案清單、Diff、自測與已知問題。不得把自測宣稱為獨立驗收，不得隱藏失敗或自行降低 AC。

### TESTER｜測試者

重新確認實際測試對象與版本，依需求與 AC 建立並實際執行正向、負向、邊界、異常測試，檢查測試能否識別缺陷，保存完整執行證據。不得只引用製作者報告，不得以預期輸出冒充實際輸出，不得把 SKIP、NOT_RUN 或 UNKNOWN 當 PASS。

### INDEPENDENT_AUDITOR｜獨立驗收者

重新讀取需求、AC、來源與交付成果，核對版本、Commit、Hash，挑戰漏測、假 PASS、未涵蓋失敗情境與文件／功能不一致，視風險重新執行測試並獨立判定。不得直接接受前兩者 PASS、未讀取成果便簽核、修改交付物使其通過、降低 AC 或以角色名稱代替證據。

## 2. MODE A｜STAGED_SELF_AUDIT

適用於一般工作、低風險、可逆修改與候選初步整理。順序固定為：

```text
IMPLEMENTER → TESTER → SELF_REVIEW
```

同一執行者可以分階段完成，但必須：三階段分開記錄、每階段保存證據、前一階段後凍結成果、下一階段重新讀取、不得引用前階段 PASS 代替新階段證據，並揭露同一執行者身分。

`STAGED_SELF_AUDIT` 不是 `INDEPENDENT_AUDITOR`，不得宣稱真正外部獨立驗收。

## 3. MODE B｜INDEPENDENTLY_AUDITED

適用於高風險工作、MIKO 正式規則修改、治理放行、Skill 正式採用、正式程式交付、正式 PR 合併前、正式版本發布與不可逆操作前。

順序固定為：

```text
IMPLEMENTER → TESTER → 冻結交付物／證據 → INDEPENDENT_AUDITOR → GOVERNANCE_RELEASE_DECISION
```

獨立驗收者必須自行讀取原始需求、AC、交付物與來源，重新檢查必要測試、尋找反例並產出獨立報告。正式放行由有權責治理者決定，不由 Skill 自行升格。

只更換對話、代理名稱或角色名稱不足以證明獨立性；高風險工作優先使用不同模型或人工驗收。冷啟動子代理只能隔離上下文，不代表消除共同偏誤。

## 4. 模式選擇矩陣

| 工作類型 | 必要模式 |
|---|---|
| 一般問答、低風險研究、一般文件整理 | STAGED_SELF_AUDIT |
| 可逆小型修改、Candidate 初步整理／技術測試 | STAGED_SELF_AUDIT |
| Candidate 正式獨立驗收 | INDEPENDENTLY_AUDITED |
| MIKO 正式規則修改、Skill 正式採用 | INDEPENDENTLY_AUDITED |
| 正式 PR 合併前、正式版本發布 | INDEPENDENTLY_AUDITED |
| 高風險權限／安全變更、不可逆操作前 | INDEPENDENTLY_AUDITED |

既有規則若要求更嚴格方式，以較嚴格者為準；不得因提供兩種模式而降低既有驗收要求。

## 5. 強制原則

1. 自驗不能取代獨立驗收。
2. TESTER 必須實際驗證。
3. INDEPENDENT_AUDITOR 必須主動反證。
4. 職責隔離與證據獨立必須可追溯。

## 6. 本候選狀態

- `STAGED_SELF_AUDIT`：可作為候選階段狀態。
- `INDEPENDENTLY_AUDITED`：只有具備獨立執行證據與治理放行決定時才能使用。
- 附約正式採用：`PENDING`。
