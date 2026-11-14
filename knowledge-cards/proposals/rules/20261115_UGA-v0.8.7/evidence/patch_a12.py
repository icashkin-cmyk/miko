#!/usr/bin/env python3
"""Patch candidate: A12 independence levels + audit packet spec (v0.2.3)."""
import re
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
DST = Path(sys.argv[2])

if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)


def rw(name, fn):
    p = DST / name
    t = p.read_text(encoding="utf-8")
    t2 = fn(t)
    assert t2 != t, f"no change in {name}"
    p.write_text(t2, encoding="utf-8")


def bump(t):
    return t.replace("version: 0.2.2", "version: 0.2.3", 1)


for f in DST.glob("*.md"):
    rw(f.name, bump)


# 1) 名詞：L0~L3 判定表
def terms(t):
    old = "| 獨立性等級 | independence level | L0 同 context；L1 同模型冷啟動（新 session、只讀驗收包）；L2 不同模型冷啟動；L3 人類驗收者 |"
    new = "| 獨立性等級 | independence level | 依 §2.1 判定表；等級以「可證明的最弱一環」為準，無法證明一律視為 L0 |"
    t = t.replace(old, new, 1)
    anchor = "| 流程先行 | process-first | 先定流程，再由流程推導標題、章節、欄位、格式、IO、AC、失敗出口 |\n"
    table = anchor + """
### 2.1 獨立性等級判定表（修正 A12-REV-01）

| 等級 | 條件（可驗證） | 必要證據 | 可給出的最高結果 | 備註 |
|---|---|---|---|---|
| L0 | 同一 session，曾載入製作內容或自我驗收結論 | 無隔離證據 | 僅 `SELF_*`；不得作為 A12 正式驗收 | 只供自查；L0 送驗一律視為未驗 |
| L1 | 同模型、新 session 冷啟動、只讀驗收包 | session 識別、模型 ID、開包前 `sha256sum -c` 輸出、`contact_with_author=false` | `AUDIT_PASS`（限文件／契約一致性） | 可作候選交付；不得作為 `ADOPTED` 的唯一依據 |
| L2 | 不同模型冷啟動（模型 ID 與製作者不同） | 同 L1，加上雙方模型 ID 對照 | `AUDIT_PASS`，可支撐 `ADOPTED` | 仍需 R-CONV 裁決 |
| L3 | 人類驗收者 | 驗收者識別（姓名或代號）、時間、簽核紀錄 | `AUDIT_PASS`，可支撐 `ADOPTED`；`EFFECTIVE` 仍需 Runtime 證據 | 利益衝突者不得擔任 |

判定規則：

- L-01 等級由「實際可證明」的最小值決定；任一條證據缺漏即降一級。
- L-02 驗收者若中途接觸作者說明、自我驗收結論或實作思路，降為 L0 並換人重驗，該輪計入 `audit_round`。
- L-03 同一人不得同時擔任 R-AUD 與 R-EVD，也不得與同一次 R-CONV 裁決同人。
- L-04 多位驗收者分歧時，以最低等級者的判定為準，交 R-CONV 裁決並記 `route_decision_reason` 同等格式的理由欄。
"""
    assert anchor in t
    return t.replace(anchor, table, 1)


rw("ucp-spec.md", terms)


# 2) A12 區塊重寫
def a12(t):
    start = t.index("### A12 獨立驗收交接")
    end = t.index("### A13 ")
    block = """### A12 獨立驗收交接
- **目的**：在可證明的隔離條件下判定產物是否符合 AC，避免自我驗收冒充獨立驗收。
- **輸入**：驗收包（規格見附錄 A）、封裝雜湊清單 `audit-packet/MANIFEST.sha256`。
- **輸出**：獨立驗收報告 `audit-report.md`（含 §附錄 A.4 固定欄位）、`audit-verify.log`、`independence_level`、逐條 AC 判定。
- **前置條件**：A11 全 `PASS`；驗收包已封裝且 `sha256sum -c` 通過；驗收者未讀取自我驗收結論、作者說明或實作思路；驗收者非 R-BLD／R-SELF／R-EVD。
- **操作要求**：先驗封裝再開包（驗證失敗即 `BLOCKED`，不得繼續）；只讀包內檔案；逐條 AC 依報告 schema 填 `verdict`、`evidence_ref`、`reason`；寫明 `independence_level`、`contact_with_author`、`reviewer_id`、`reviewed_at`、`tool_versions`；等級依 §2.1 以最弱一環判定。
- **禁止事項**：不得由 R-BLD／R-SELF 兼任；不得先看自我驗收結論；不得修改包內任何檔案；L0 不得給 `AUDIT_PASS`；不得把 `AUDIT_PASS` 寫成 `ADOPTED` 或 `EFFECTIVE`（`ADOPTED` 需 R-CONV 裁決）。
- **檢查點**：封裝雜湊一致；報告欄位齊全；每條 AC 有判定與證據引用；等級與證據相符；`contact_with_author=false`。
- **Acceptance Criteria**：`AC-A12-01` 驗收者隔離且 `independence_level ≥ L1`；`AC-A12-02` 逐條 AC 有判定與證據引用；`AC-A12-03` 標籤與等級一致；`AC-A12-04` 封裝驗證通過且報告欄位齊全；`AC-A12-05` 接觸作者或包內竄改一律不得 `AUDIT_PASS`；`AC-A12-06` `AUDIT_PASS` 未經 R-CONV 不得標 `ADOPTED`／`EFFECTIVE`。
- **Failure Handling**：`AUDIT_FAIL` → 回 A10 並 `audit_round+1`；封裝雜湊不符或包內缺件 → `BLOCKED`，原報告作廢、重新封裝；驗收者接觸作者 → 降 L0、換人重驗並 `audit_round+1`；無合格驗收者 → `BLOCKED`（不得降格為自我驗收）。
- **Recovery**：修正後由 R-EVD 重新封裝（新 `packet_version`、新雜湊）再送驗；上限 2 輪；重驗不得沿用舊報告。
- **Regression Test**：`RT-A12` 五題：①故意缺欄位版本送驗 → 必須 `AUDIT_FAIL`；②L0 送驗 → 不得回 `AUDIT_PASS`；③封裝後改一個位元組 → 必須 `BLOCKED`；④L1 驗收者中途讀取自我驗收結論 → 必須降 L0 並重驗；⑤`AUDIT_PASS` 後直接標 `ADOPTED` → 必須被 TSV-AUDIT 判 `FAIL`。
- **閉環條件**：`AUDIT_PASS` 且 `audit_round ≤ 2` 且等級 ≥ L1 且封裝驗證通過且報告欄位齊全。
- **負責角色**：R-AUD（不得兼 R-EVD、不得與同次 R-CONV 同人）。
- **證據與保存方式**：`evidence/<task_id>/audit-report.md`、`audit-verify.log`、`audit-packet/MANIFEST.sha256`；報告與封裝清單一併入交付包，不得事後修改。
"""
    return t[:start] + block + t[end:]


rw("ucp-spec.md", a12)


# 3) 附錄 A：驗收包規格
def appendix(t):
    anchor = "## 12. 未決事項"
    app = """## 附錄 A：驗收包規格（修正 A12-REV-03）

### A.1 正面清單

驗收包目錄固定為 `audit-packet/`，只允許下列檔案；多一個檔即不合格。

```
audit-packet/
├── MANIFEST.sha256          # 包內所有檔案的雜湊，第一行固定為本清單自身以外的全部檔案
├── packet-meta.yaml         # packet_version、task_id、封裝者、封裝時間、契約版本、產物版本
├── artifact/                # 候選產物正本（不含作者註解）
├── ac/ac-table.md           # AC 表（來源：UAC §12 或 USC-C8，附版本）
├── contract/                # 契約版本（uac-spec.md 或 usc-spec.md 的對應版本）
├── diff/round-<n>.patch     # 只保留 unified diff 內容，去除 commit message、註解與作者說明
└── checks/                  # 檢查器原始輸出（JSON），不得含作者評語或自我驗收結論
```

### A.2 排除清單

不得放入：作者辯解、自我驗收結論、實作思路、對話紀錄、待辦清單、未來計畫。diff 若含上述內容，必須先去除再封裝。

### A.3 封裝與驗證

1. R-EVD 依 A.1 建包，`packet-meta.yaml` 記 `packet_version`（`pkt-<YYYYMMDD>T<HHMMSS+0800>-v<semver>`）。
2. 對包內所有檔案計算 SHA-256 寫入 `MANIFEST.sha256`（格式同 `sha256sum`）。
3. 驗收者開包前執行 `sha256sum -c audit-packet/MANIFEST.sha256`，輸出存 `audit-verify.log`；任一 `FAILED` 即 `BLOCKED`。
4. 驗收者不得寫入包內；若需註記，一律寫在包外的 `audit-report.md`。

### A.4 驗收報告固定欄位

| 欄位 | 說明 |
|---|---|
| `task_id`、`packet_version` | 對應封裝 |
| `reviewer_id`、`reviewer_model`、`reviewed_at` | 驗收者與時間 |
| `independence_level` | L0～L3，依 §2.1 判定 |
| `contact_with_author` | `true`／`false`；`true` 時必須降 L0 |
| `manifest_check` | `PASS`／`FAIL` |
| `tool_versions` | 檢查器與模型版本 |
| `results[]` | 每條 AC：`ac_id`、`verdict`、`evidence_ref`、`reason` |
| `overall` | `AUDIT_PASS`／`AUDIT_FAIL`／`BLOCKED` |
| `adoption_recommendation` | `NONE`／`RECOMMEND_ADOPT`（僅建議，`ADOPTED` 由 R-CONV 裁決） |

### A.5 竄改與作廢

封裝雜湊不符、包內缺件或出現排除清單內容時，該報告作廢，重新封裝並 `audit_round+1`；不得以口頭說明補正。

## 12. 未決事項"""
    assert anchor in t
    return t.replace(anchor, app, 1)


rw("ucp-spec.md", appendix)


# 4) §9 證據、§10 彙總、角色表
def misc(t):
    t = t.replace(
        "證據存於 `evidence/<task_id>/`；驗收包另存 `audit-packet/`，只含候選產物、AC、契約、diff、檢查器輸出。驗收包封裝後計算 SHA-256，驗收者不得修改。",
        "證據存於 `evidence/<task_id>/`；驗收包另存 `audit-packet/`，內容與封裝依附錄 A。封裝後計算 SHA-256，驗收者開包前必須驗證且不得修改。")
    t = t.replace("見第 5 節，共 42 條（每步 3 條）。", "見第 5 節，共 45 條（A00～A11、A13 每步 3 條，A12 共 6 條）。")
    t = t.replace("| R-AUD | 獨立驗收 | 不得為 R-BLD／R-SELF；須 `independence_level ≥ L1` |",
                  "| R-AUD | 獨立驗收 | 不得為 R-BLD／R-SELF／R-EVD；不得與同次 R-CONV 同人；須 `independence_level ≥ L1` |")
    t = t.replace("| UCP-OPEN-02 | 正式採用是否要求 L3（人類）驗收 | PENDING_DECISION（候選交付最低 L1；採用正本建議 L3） |",
                  "| UCP-OPEN-02 | 正式採用是否要求 L3（人類）驗收 | PENDING_DECISION（候選交付最低 L1；`ADOPTED` 最低 L2；正本建議 L3） |")
    return t


rw("ucp-spec.md", misc)


# 5) TSV：新增 TSV-AUDIT
def tsv(t):
    t = t.replace("定義十一個檢查器", "定義十二個檢查器")
    t = t.replace("| TSV-REGRESSION | 回歸集 | `SELF_FAIL` |",
                  "| TSV-AUDIT | 驗收包與獨立性（附錄 A、§2.1） | `SELF_FAIL` |\n| TSV-REGRESSION | 回歸集 | `SELF_FAIL` |")
    t = t.replace("`AC-TSV-01` 十一個檢查器皆可執行；", "`AC-TSV-01` 十二個檢查器皆可執行；")
    return t


rw("modules-spec.md", tsv)

# 6) 驗收矩陣
def matrix(t):
    t = t.replace("""| A12 | AC-A12-01 驗收者隔離 ≥L1 | 人工檢視 | Claude API 冷啟動（L2） | R-AUD | `NOT_RUN` |""",
                  """| A12 | AC-A12-01 驗收者隔離 ≥L1 | 人工檢視 | Claude API 冷啟動（L2） | R-AUD | `NOT_RUN` |
| A12 | AC-A12-04 封裝驗證與報告欄位齊全 | TSV-AUDIT | 附錄 A.4 欄位 | R-SELF | `PASS` |
| A12 | AC-A12-05 接觸作者或竄改不得 PASS | TSV-AUDIT | A12 禁止事項與失敗處理 | R-SELF | `PASS` |
| A12 | AC-A12-06 PASS 未經 R-CONV 不得標 ADOPTED | TSV-AUDIT | A12 禁止事項 | R-SELF | `PASS` |""")
    t = t.replace("統計：`PASS` 22 條、`NOT_RUN` 20 條、`UNKNOWN` 0 條、`BLOCKED` 0 條。",
                  "統計：`PASS` 25 條、`NOT_RUN` 20 條、`UNKNOWN` 0 條、`BLOCKED` 0 條（共 45 條）。")
    t = t.replace("`PASS`（tsv_check.py 10 個＋regression.py 1 個）", "`PASS`（tsv_check.py 11 個＋regression.py 1 個）")
    return t


rw("acceptance-matrix.md", matrix)
print("patched", DST)
