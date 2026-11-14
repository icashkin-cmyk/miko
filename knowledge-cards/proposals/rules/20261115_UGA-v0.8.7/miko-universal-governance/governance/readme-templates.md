---
doc_id: uga-readme-templates
name_en: Module README Templates
name_zh: 各模組 README 模板
module: governance
version: 0.8.7
date: 2026-11-14
status: PROPOSED
---

# 各模組 README 模板

每個模組的 `README.md` 一律使用同一骨架，只替換標示欄位。狀態列固定含 `Runtime: UNKNOWN`（除非有 LCV H-04 三項證據）。

## 共用骨架

```markdown
# <模組繁中名>（<Module English Name>）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
<一段話說明此模組唯一負責什麼>

## 範圍與非範圍
- 範圍：<...>
- 非範圍：<...>（由 <其他模組> 負責）

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|

## 與其他模組的關係
- 上游（本模組依賴）：<模組與版本>
- 下游（依賴本模組）：<模組與版本>

## 使用方式
<呼叫順序、輸入、輸出>

## 驗收方式
<AC 清單、檢查器 ID、通過門檻>

## 失敗與回復
<失敗出口、重試上限、回復路徑>

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 1. governance/README.md

```markdown
# 治理層（Governance Layer）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
定義 A0 硬邊界、W1～W7 工作契約與 A3 狀態字典；本模組為唯一擁有者。

## 範圍與非範圍
- 範圍：停止／禁止閘門、任務分類、四態、交接契約。
- 非範圍：製作順序（UCP）、欄位（UAC／USC）。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| gov-index.md | 治理索引 | <x.y.z> |
| gov-states.md | A3 狀態字典 | <x.y.z> |
| gov-handoff.md | W6／W7 交接契約 | <x.y.z> |
| VERSION | 版本檔 | <x.y.z> |

## 與其他模組的關係
- 上游：miko-core 正本（版本 <v>）
- 下游：UCP、所有產物

## 使用方式
每個任務開頭讀取；狀態判定一律引用 gov-states.md。

## 驗收方式
TSV-CONTRACT；狀態字典須與 UCP §7 完全一致。

## 失敗與回復
核心未載入 → `CORE_NOT_READ`；狀態衝突 → `CONFLICT` 交 R-CONV。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 2. universal-creation-process/README.md

```markdown
# 通用製作流程（Miko Creation Process, MCP）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
所有產物共用的製作主幹 A00～A13 與閉環。

## 範圍與非範圍
- 範圍：順序、閉環、預算、失敗出口、獨立驗收門檻、證據。
- 非範圍：章節與欄位（UAC／USC）。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| ucp-spec.md | 主規格 | <x.y.z> |
| ucp-steps.yaml | 14 步 × 13 欄機讀定義（回歸為例外） | <x.y.z> |
| ucp-roles.md | 角色與兼任限制 | <x.y.z> |

## 與其他模組的關係
- 上游：GOV、RSL、TSV
- 下游：所有產物

## 使用方式
從 A00 開始，依序執行；A11 上限 3 輪、A12 上限 2 輪。

## 驗收方式
TSV-STRUCT（14 步 × 13 欄，回歸為例外）、TSV-EXIT（失敗出口）、TSV-REG（預算與終止）。

## 失敗與回復
見 ucp-spec §7；超限即 `BLOCKED` 並出困難卡。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 3. universal-artifact-contract/README.md

```markdown
# 通用產物契約（Document Contract, DOC）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
規定規格書、架構書、流程設計書、治理文件、路由器文件、測試規格、整合升級文件的十六章與必要欄位。

## 範圍與非範圍
- 範圍：章節、欄位、欄位格式。
- 非範圍：製作順序（UCP）、Skill 格式（USC）。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| uac-spec.md | 十六章規格 | <x.y.z> |
| uac-template.md | 空白模板 | <x.y.z> |
| uac-chapters.yaml | 機讀章節欄位 | <x.y.z> |

## 與其他模組的關係
- 上游：無（僅引用 UCP 步驟 ID）
- 下游：RSL、LCV、TSV、所有規格類產物

## 使用方式
UCP A03 鎖定欄位；A05 依本章程實例化。

## 驗收方式
TSV-CONTRACT（十六章必要欄位逐一比對）。

## 失敗與回復
缺章 → `SELF_FAIL`；欄位衝突 → 以本章為準（附錄 B）。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 4. universal-skill-contract/README.md

```markdown
# 通用 Skill 契約（Skill Contract, SKL）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
規定 Skill 的九項必要契約、四節格式、P/C/J 七欄步驟表。

## 範圍與非範圍
- 範圍：Skill 文件結構與必要內容。
- 非範圍：十六章（UAC）、製作順序（UCP）。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| usc-spec.md | 九契約／四節／七欄 | <x.y.z> |
| usc-template.md | Skill 空白模板 | <x.y.z> |
| usc-contracts.yaml | 機讀契約定義 | <x.y.z> |

## 與其他模組的關係
- 上游：無（引用 UCP 步驟 ID）
- 下游：skills/、adapters/

## 使用方式
Skill 建置前先鎖定九契約，再依四節撰寫。

## 驗收方式
TSV-SKILL（九契約、四節、七欄、expected／forbidden）。

## 失敗與回復
缺契約 → `SELF_FAIL`；七欄缺一 → 不合格。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 5. routing-and-selection/README.md

```markdown
# 路由與選擇（Routing and Selection, RSL）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
把產物類型映射到契約與驗收器。

## 範圍與非範圍
- 範圍：路由表、判定規則、衝突裁決。
- 非範圍：流程內容、欄位內容。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| rsl-spec.md | 路由規格 | <x.y.z> |
| rsl-routes.yaml | 機讀路由表 | <x.y.z> |

## 與其他模組的關係
- 上游：UAC、USC
- 下游：UCP A02

## 使用方式
依 artifact_type 查表；命中兩條即 `CONFLICT`。

## 驗收方式
TSV-ROUTE（唯一性、完整性、驗收器存在）。

## 失敗與回復
路由表不可讀 → `NOT_READ`，停 A02。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 6. lifecycle-and-versioning/README.md

```markdown
# 生命週期與版本（Lifecycle and Versioning, LCV）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
規定版本、快照、退役、熱插拔宣告。

## 範圍與非範圍
- 範圍：SemVer、狀態升格、退役、熱插拔證據。
- 非範圍：欄位內容、流程步驟。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| lcv-spec.md | 版本與狀態規格 | <x.y.z> |
| lcv-naming.md | 檔名與快照命名 | <x.y.z> |
| lcv-retirement.md | 退役規則 | <x.y.z> |

## 與其他模組的關係
- 上游：UAC
- 下游：ARC、所有產物

## 使用方式
每次版本變更依 V-01～V-06；退役依 RT-01～RT-05。

## 驗收方式
TSV-REG（狀態、退役、命名、MANIFEST）。

## 失敗與回復
缺快照 → 不得退役；無 H-04 證據 → 維持 `UNKNOWN`。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 7. testing-and-validation/README.md

```markdown
# 測試與驗證（Testing and Validation, TSV）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
定義十一個檢查器與回歸測試，作為交付門檻。

## 範圍與非範圍
- 範圍：檢查器、門檻、結果格式。
- 非範圍：製作流程、欄位定義。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| tsv-spec.md | 檢查器規格 | <x.y.z> |
| tsv-matrix.md | 驗收矩陣 | <x.y.z> |

## 與其他模組的關係
- 上游：UAC、USC
- 下游：tests/

## 使用方式
`tsv_check.py <candidate> <out.json>`；全部 PASS 才可交付。

## 驗收方式
TSV-REGRESSION（負向注入測試）。

## 失敗與回復
任一 `FAIL` → 回 A10；`NOT_RUN` 視為未通過。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 8. skills/README.md

```markdown
# Skills（SKL）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
存放符合 USC 的 Skill。

## 範圍與非範圍
- 範圍：Skill 實作與測試。
- 非範圍：契約定義（USC）、路由（RSL）。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| <skill>/SKILL.md | Skill 主檔（四節） | <x.y.z> |
| <skill>/VERSION | 版本 | <x.y.z> |
| <skill>/CHANGELOG.md | 變更紀錄 | — |

## 與其他模組的關係
- 上游：USC、UCP
- 下游：adapters/

## 使用方式
依 USC 四節撰寫；P/C/J 步驟表為必備。

## 驗收方式
TSV-SKILL + 各 Skill 自帶測題。

## 失敗與回復
缺測題 → 不得採用；行為 FAIL → 回 A10。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 9. adapters/README.md

```markdown
# Adapters（ADP）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
定義與各執行環境（Claude Code、Manus、GitHub、generic）的介面約定。

## 範圍與非範圍
- 範圍：介面定義、相容性檢查、回滾程序。
- 非範圍：實際整合實作；目前全部為 PLACEHOLDER。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| claude-code/ | 介面定義（未實測） | PLACEHOLDER |
| manus/ | 介面定義（未實測） | PLACEHOLDER |
| github/ | 介面定義（未實測） | PLACEHOLDER |
| generic/ | 通用介面 | PLACEHOLDER |

## 與其他模組的關係
- 上游：USC、LCV
- 下游：無（尚未實作）

## 使用方式
不得宣稱已支援；升格需 LCV H-04 三項證據。

## 驗收方式
TSV-RUNTIME。

## 失敗與回復
無證據 → `UNKNOWN`；替換失敗 → 回滾至前一 adapter。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 10. tests/README.md

```markdown
# Tests（TST）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
存放檢查器、fixtures 與回歸測試。

## 範圍與非範圍
- 範圍：單元、契約、整合、回歸測試。
- 非範圍：規格內容。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| unit/ | 檢查器單元測試 | — |
| contract/ | 契約符合性測試 | — |
| regression/ | 負向注入回歸 | — |
| fixtures/ | 測資 | — |

## 與其他模組的關係
- 上游：TSV
- 下游：無

## 使用方式
`pytest tests/` 或直接執行腳本；結果寫入 results/。

## 驗收方式
全數 `PASS`；任一 `NOT_RUN` 視為未通過。

## 失敗與回復
失敗 → 回 A10 修正後重跑。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```

## 11. archive/README.md

```markdown
# Archive（ARC）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
保存不可變快照、退役文件與 ADR。

## 範圍與非範圍
- 範圍：snapshots/、retired/、decisions/。
- 非範圍：現行正本。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| snapshots/ | 版本快照（N-05 命名） | — |
| retired/ | 退役文件與 redirect 表 | — |
| decisions/ | ADR | — |

## 與其他模組的關係
- 上游：LCV
- 下游：無

## 使用方式
只新增，不修改、不刪除。

## 驗收方式
TSV-REG（快照命名、MANIFEST）。

## 失敗與回復
快照遺失 → `BLOCKED`，不得宣稱已保存。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
```
