#!/usr/bin/env python3
"""v0.4.0: add LITE path (附錄 C) + AC-A00-05."""
import shutil
import sys
from pathlib import Path

SRC, DST = Path(sys.argv[1]), Path(sys.argv[2])
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

for f in list(DST.glob("*.md")) + [DST / "VERSION"]:
    t = f.read_text(encoding="utf-8")
    f.write_text(t.replace("0.3.1", "0.4.0", 1), encoding="utf-8")

c = DST / "contract.yaml"
c.write_text(c.read_text(encoding="utf-8").replace("version: 0.3.1", "version: 0.4.0", 1), encoding="utf-8")

p = DST / "ucp-spec.md"
t = p.read_text(encoding="utf-8")
t = t.replace("`AC-A00-04` 治理、錯誤帳、否決帳皆有載入結果或未讀原因。",
              "`AC-A00-04` 治理、錯誤帳、否決帳皆有載入結果或未讀原因；`AC-A00-05` 若判定為輕量路徑，理由齊全且不在禁止清單。", 1)
t = t.replace("共 48 條（A00、A10、A13 各 4 條", "共 49 條（A00 5 條、A10 與 A13 各 4 條", 1)

appendix = """## 附錄 C：輕量路徑（LITE）

輕量路徑是給低風險、低影響、單一檔案、可逆、且不涉及跨平台寫入的產物用的縮減流程。它的目的不是降低標準，而是避免小任務被整套流程擋住而選擇繞過治理。判定發生在 A00：請求同時滿足五個條件才可走 LITE，五個條件是單一產物、可逆、不涉及治理規則或 Skill 正本、不涉及契約修改、不涉及跨平台寫入。

LITE 保留的步驟是 A00 分級、A01 讀來源、A03 鎖欄位、A06 定 AC、A08 自我驗收、A13 交付。可以省略的是 A04 流程先行、A05 結構實例化、A07 失敗出口、A09 主動補強、A11 有界重測、A12 獨立驗收；A10 只保留一句 diff 說明，不要求完整 patch。省略的每一步都要在任務卡寫明省略理由，不能只寫「簡化」。

禁止走 LITE 的範圍是：治理規則、Skill 正本、契約與路由文件、跨平台寫入、任何不可逆操作、以及會影響多個專案的變更。這些一律走完整路徑，沒有例外。

中途升級的規則是：一旦發現請求涉及禁止範圍，立刻升級為完整路徑並補跑缺少的步驟，已完成的步驟不重做；升級時在變更帳寫一筆，記錄升級原因與補跑清單。

LITE 的驗收條件是 AC-A00-05：判定為 LITE 時，五個條件逐條有理由，且不在禁止清單內。因為 LITE 省略獨立驗收，LITE 產物不得標為已採用，只能作為草稿或參考；要進正本或標已採用，必須補跑完整路徑。

## 12. 未決事項"""
t = t.replace("## 12. 未決事項", appendix, 1)
t = t.replace("| UCP-OPEN-04 | 修正帳本未讀時是否阻擋開工（目前為可繼續但須列未讀） | PENDING_DECISION |",
              "| UCP-OPEN-04 | 修正帳本未讀時是否阻擋開工（目前為可繼續但須列未讀） | PENDING_DECISION |\n| UCP-OPEN-05 | LITE 的「低風險」是否要改成可量化門檻（例如行數、影響檔案數） | PENDING_DECISION |", 1)
p.write_text(t, encoding="utf-8")

m = DST / "acceptance-matrix.md"
t = m.read_text(encoding="utf-8")
t = t.replace("| A00 | AC-A00-04 三份常駐文件有載入結果 | 行為觀察 | task-card 載入區塊 | R-AUD | `NOT_RUN` |",
              "| A00 | AC-A00-04 三份常駐文件有載入結果 | 行為觀察 | task-card 載入區塊 | R-AUD | `NOT_RUN` |\n| A00 | AC-A00-05 LITE 判定有理由且不在禁止清單 | 人工檢視 | task-card 分級區塊 | R-AUD | `NOT_RUN` |")
t = t.replace("統計：`PASS` 26 條、`NOT_RUN` 22 條、`UNKNOWN` 0 條、`BLOCKED` 0 條（共 48 條）。",
              "統計：`PASS` 26 條、`NOT_RUN` 23 條、`UNKNOWN` 0 條、`BLOCKED` 0 條（共 49 條）。")
m.write_text(t, encoding="utf-8")
print("patched", DST)
