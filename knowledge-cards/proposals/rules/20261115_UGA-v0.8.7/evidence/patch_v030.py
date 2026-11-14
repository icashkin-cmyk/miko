#!/usr/bin/env python3
"""v0.3.0: integrate correction ledger into UCP/UAC/RSL/TSV + tests."""
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
DST = Path(sys.argv[2])

keep = (DST / "ledger-spec.md").read_text(encoding="utf-8")
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)
(DST / "ledger-spec.md").write_text(keep, encoding="utf-8")


def rw(name, pairs):
    p = DST / name
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert old in t, (name, old[:60])
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")


for f in DST.glob("*.md"):
    t = f.read_text(encoding="utf-8")
    f.write_text(t.replace("version: 0.2.4", "version: 0.3.0", 1), encoding="utf-8")

rw("ucp-spec.md", [
    ("| 流程先行 | process-first | 先定流程，再由流程推導標題、章節、欄位、格式、IO、AC、失敗出口 |",
     "| 流程先行 | process-first | 先定流程，再由流程推導標題、章節、欄位、格式、IO、AC、失敗出口 |\n"
     "| 修正帳本 | correction ledger | `ledger/` 下的錯誤帳、否決帳、變更帳與索引；開工時與治理一起載入 |\n"
     "| 錯誤紀錄 | error entry | 錯誤帳的一筆，含現象、證據、根因、修正與回歸測題，以去重鍵判重 |\n"
     "| 否決紀錄 | rejection entry | 否決帳的一筆，含被否決方案、理由、替代方案與解除條件 |\n"
     "| 文本純度 | text purity | 正文只放已驗收合格的繁中敘述，測試輸出與原始日誌只放證據目錄 |"),
    ("- **輸入**：使用者請求原文、對話上下文、治理核心狀態（版本或 `CORE_NOT_READ`）。",
     "- **輸入**：使用者請求原文、對話上下文、治理核心狀態（版本或 `CORE_NOT_READ`）、修正帳本（錯誤帳與否決帳）。"),
    ("- **前置條件**：可讀取使用者請求；已判定治理核心狀態。",
     "- **前置條件**：可讀取使用者請求；已判定治理核心狀態；治理、錯誤帳、否決帳三份常駐文件已依序載入或已標未讀。"),
    ("- **操作要求**：逐條拆解請求；標記不可逆操作與硬禁止（下單、LIVE、Broker、外部寫入）；核心未載入時標 `CORE_NOT_READ` 並限制為候選輸出；初始化兩個計數器。",
     "- **操作要求**：先依治理、錯誤帳、否決帳的順序載入常駐文件並記下版本與雜湊；再逐條拆解請求；標記不可逆操作與硬禁止（下單、LIVE、Broker、外部寫入）；核心未載入時標 `CORE_NOT_READ` 並限制為候選輸出；初始化兩個計數器。"),
    ("- **檢查點**：任務卡逐條覆蓋請求；禁止項與授權狀態已列；計數器已初始化。",
     "- **檢查點**：三份常駐文件有載入結果；任務卡逐條覆蓋請求；禁止項與授權狀態已列；計數器已初始化。"),
    ("`AC-A00-03` 核心狀態與計數器已標示。",
     "`AC-A00-03` 核心狀態與計數器已標示；`AC-A00-04` 治理、錯誤帳、否決帳皆有載入結果或未讀原因。"),
    ("- **證據與保存方式**：`evidence/<task_id>/task-card.md`（含時間戳與 SHA-256）。",
     "- **證據與保存方式**：`evidence/<task_id>/task-card.md`（含時間戳、載入結果與 SHA-256）。"),
    ("- **輸出**：unified diff、變更紀錄（原因、位置、影響的 AC）。",
     "- **輸出**：unified diff、變更紀錄（原因、位置、影響的 AC）、修正帳本更新（錯誤帳、變更帳）。"),
    ("- **操作要求**：每筆變更對應至少一個 AC 或缺口 ID；不得覆寫歷史版本。",
     "- **操作要求**：每筆變更對應至少一個 AC 或缺口 ID；先算去重鍵，命中既有條目就地更新並保留前一版，未命中才新增；不得覆寫歷史版本。"),
    ("`AC-A10-03` 歷史版本未被覆寫。",
     "`AC-A10-03` 歷史版本未被覆寫；`AC-A10-04` 變更帳已就地更新且對應 diff 與證據。"),
    ("- **輸出**：交付包、MANIFEST、收工報告（任務四態、困難卡、未驗證清單、聲明）。",
     "- **輸出**：交付包、MANIFEST、收工報告（任務四態、困難卡、未驗證清單、聲明）、修正帳本快照。"),
    ("`AC-A13-03` 未驗證清單與困難卡已列。",
     "`AC-A13-03` 未驗證清單與困難卡已列；`AC-A13-04` 三份帳的快照與雜湊已入交付包。"),
    ("見第 5 節，共 45 條（A00～A11、A13 每步 3 條，A12 共 6 條）。",
     "見第 5 節，共 48 條（A00、A10、A13 各 4 條，A12 共 6 條，其餘每步 3 條）。"),
    ("| UCP-OPEN-03 | 預算重置的正式授權格式 | PENDING_DECISION |",
     "| UCP-OPEN-03 | 預算重置的正式授權格式 | PENDING_DECISION |\n| UCP-OPEN-04 | 修正帳本未讀時是否阻擋開工（目前為可繼續但須列未讀） | PENDING_DECISION |"),
])

rw("uac-spec.md", [
    ("本契約只規定「必須有哪些章節與欄位」，不規定製作順序（由 UCP 規定）。",
     "本契約只規定「必須有哪些章節與欄位」，不規定製作順序（由 UCP 規定）。正文一律使用已驗收合格的繁體中文敘述，測試輸出、原始日誌、模型評語與待辦碎片不得寫入正文，只能放在證據目錄並以文件識別與驗收條件編號引用，此為文本純度規則（對應修正帳本規格第 2 章）。"),
])

rw("modules-spec.md", [
    ("| RSL-R09 | Adapter 介面文件 | UAC | TSV-CONTRACT + TSV-RUNTIME | Runtime 狀態須為 `UNKNOWN` 或附證據 |",
     "| RSL-R09 | Adapter 介面文件 | UAC | TSV-CONTRACT + TSV-RUNTIME | Runtime 狀態須為 `UNKNOWN` 或附證據 |\n| RSL-R10 | 修正帳本文件 | UAC | TSV-CONTRACT + TSV-LEDGER | 三帳、載入順序、去重與熱插拔介面齊全 |"),
    ("定義檢查器與測試集", "定義十三個檢查器與測試集"),
    ("| TSV-AUDIT | 驗收包與獨立性（附錄 A、§2.1） | `SELF_FAIL` |",
     "| TSV-AUDIT | 驗收包與獨立性（附錄 A、§2.1） | `SELF_FAIL` |\n| TSV-LEDGER | 修正帳本（三帳、載入順序、去重、文本純度） | `SELF_FAIL` |"),
    ("`AC-TSV-01` 十二個檢查器皆可執行；", "`AC-TSV-01` 十三個檢查器皆可執行；"),
])

s = (DST / "contract.yaml").read_text(encoding="utf-8")
s = s.replace("version: 0.2.4", "version: 0.3.0", 1)
s = s.replace("  - {route_id: RSL-R09, artifact: adapter-doc, contract: UAC, checker: [TSV-CONTRACT, TSV-RUNTIME]}",
              "  - {route_id: RSL-R09, artifact: adapter-doc, contract: UAC, checker: [TSV-CONTRACT, TSV-RUNTIME]}\n"
              "  - {route_id: RSL-R10, artifact: correction-ledger, contract: UAC, checker: [TSV-CONTRACT, TSV-LEDGER]}")
(DST / "contract.yaml").write_text(s, encoding="utf-8")

rw("acceptance-matrix.md", [
    ("| A00 | AC-A00-03 核心狀態與計數器已標 | 文件檢視 | 本文件 front matter `runtime_verified` | R-SELF | `PASS` |",
     "| A00 | AC-A00-03 核心狀態與計數器已標 | 文件檢視 | 本文件 front matter `runtime_verified` | R-SELF | `PASS` |\n| A00 | AC-A00-04 三份常駐文件有載入結果 | 行為觀察 | task-card 載入區塊 | R-AUD | `NOT_RUN` |"),
    ("| A10 | AC-A10-03 歷史未覆寫 | 檔案檢視 | v0.1、v0.2 保留 | R-SELF | `PASS` |",
     "| A10 | AC-A10-03 歷史未覆寫 | 檔案檢視 | v0.1、v0.2 保留 | R-SELF | `PASS` |\n| A10 | AC-A10-04 變更帳就地更新並對應 diff | TSV-LEDGER | ledger-spec 第 5 章 | R-SELF | `PASS` |"),
    ("| A13 | AC-A13-03 未驗證與困難卡已列 | 文件檢視 | 收工報告 | R-SELF | `PASS` |",
     "| A13 | AC-A13-03 未驗證與困難卡已列 | 文件檢視 | 收工報告 | R-SELF | `PASS` |\n| A13 | AC-A13-04 三帳快照與雜湊入交付包 | 行為觀察 | 尚未實作封裝 | R-AUD | `NOT_RUN` |"),
    ("統計：`PASS` 25 條、`NOT_RUN` 20 條、`UNKNOWN` 0 條、`BLOCKED` 0 條（共 45 條）。",
     "統計：`PASS` 26 條、`NOT_RUN` 22 條、`UNKNOWN` 0 條、`BLOCKED` 0 條（共 48 條）。"),
    ("`PASS`（tsv_check.py 11 個＋regression.py 1 個）", "`PASS`（tsv_check.py 12 個＋regression.py 1 個）"),
])
print("patched", DST)
