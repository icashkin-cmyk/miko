---
doc_id: uga-structure
name_en: MIKO Universal Governance Architecture - Structure, Naming and Templates
name_zh: MIKO 通用治理架構－結構、命名與模板
module: governance
version: 0.8.7
date: 2026-11-14
status: PROPOSED
supersedes: 0.1.0
amends: 0.8.7
runtime_verified: UNKNOWN
---

# MIKO Universal Governance Architecture：結構、命名與模板 v0.8.7

## 1. 總目錄

```
MIKO Universal Governance Architecture
├─ 0 治理層（GOV）
│   ├─ 0.1 A0 硬邊界與任務分類
│   ├─ 0.2 W1～W7 工作契約
│   └─ 0.3 A3 狀態字典
├─ A 通用製作流程（UCP）
│   ├─ A.1 主幹 A00～A13
│   ├─ A.2 閉環與預算
│   ├─ A.3 獨立驗收與獨立性等級
│   └─ A.4 證據、困難卡與任務四態
├─ 契約層
│   ├─ 文件契約（DOC，原 UAC）：十六章
│   └─ Skill 契約（SKL，原 USC）：九契約、四節、七欄
├─ 橫向服務層
│   ├─ 路由與選擇（RSL）
│   ├─ 生命週期與版本（LCV）
│   └─ 測試與驗證（TSV）
├─ 實作層
│   ├─ Skills（SKL）
│   └─ Adapters（ADP，全部為 PLACEHOLDER／UNKNOWN）
└─ 支撐層
    ├─ Tests（TST）
    └─ Archive（ARC）
```

## 2. GitHub 資料夾結構

```
miko-universal-governance/
├── README.md
├── VERSION
├── MANIFEST.sha256
├── governance/
│   ├── README.md
│   ├── VERSION
│   ├── gov-index.md
│   ├── gov-states.md
│   ├── gov-handoff.md
│   └── snapshots/
├── universal-creation-process/
│   ├── README.md
│   ├── VERSION
│   ├── ucp-spec.md
│   ├── ucp-steps.yaml
│   ├── ucp-roles.md
│   └── snapshots/
├── universal-artifact-contract/
│   ├── README.md
│   ├── VERSION
│   ├── uac-spec.md
│   ├── uac-template.md
│   ├── uac-chapters.yaml
│   └── snapshots/
├── universal-skill-contract/
│   ├── README.md
│   ├── VERSION
│   ├── usc-spec.md
│   ├── usc-template.md
│   ├── usc-contracts.yaml
│   └── snapshots/
├── routing-and-selection/
│   ├── README.md
│   ├── VERSION
│   ├── rsl-spec.md
│   ├── rsl-routes.yaml
│   └── snapshots/
├── lifecycle-and-versioning/
│   ├── README.md
│   ├── VERSION
│   ├── lcv-spec.md
│   ├── lcv-naming.md
│   ├── lcv-retirement.md
│   └── snapshots/
├── testing-and-validation/
│   ├── README.md
│   ├── VERSION
│   ├── tsv-spec.md
│   ├── tsv-matrix.md
│   └── snapshots/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── VERSION
│       ├── CHANGELOG.md
│       └── tests/
├── adapters/
│   ├── README.md            # 明示：全部為 PLACEHOLDER，狀態 UNKNOWN
│   ├── claude-code/         # 僅介面定義，未經 Runtime 實測
│   ├── manus/               # 僅介面定義，未經 Runtime 實測
│   ├── github/              # 僅介面定義，未經 Runtime 實測
│   └── generic/             # 僅介面定義，未經 Runtime 實測
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   ├── regression/
│   └── fixtures/
└── archive/
    ├── snapshots/
    ├── retired/
    └── decisions/           # ADR
```

### 2.1 Adapter 狀態聲明（修正 F-04、F-05）

`adapters/` 下所有資料夾目前皆為 **PLACEHOLDER**：只有介面約定，沒有 Runtime 實測證據。狀態一律 `UNKNOWN`，不得解讀為 Claude Code、Manus 或 GitHub 已支援熱插拔。任何升格為 `VERIFIED` 必須附 LCV H-04 三項證據。

## 3. 檔名規則

| 規則 | 內容 |
|---|---|
| N-01 | 資料夾：小寫 kebab-case，僅 `a-z0-9-` |
| N-02 | 正式正本：`<module>-<doctype>.md`，不含版本與日期；版本記於 `VERSION` 與 front matter |
| N-03 | 機讀檔：`.yaml`，與同名 `.md` 成對 |
| N-04 | ADR：`ADR-<NNN>-<slug>.md` |
| N-05 | 快照：`<doc-id>__<YYYY-MM-DD>T<HHMMSS+0800>__v<semver>__c<commit7>__s<sha256前12>.md` |
| N-06 | 英文穩定識別名：`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`；繁中名稱置於 `name_zh`，不得只有繁中檔名 |
| N-07 | 正式正本與快照差異：正本無時間戳、可覆寫並由 git 追蹤；快照不可變、含時間、commit、hash |
| N-08 | 測試檔：`test_<checker>_<case>.py` |

## 4. 版本、日期、時間、commit、SHA-256 與退役

| 項目 | 規則 |
|---|---|
| 版本 | SemVer 2.0.0；MAJOR／MINOR／PATCH 見 LCV |
| 日期 | `YYYY-MM-DD` |
| 時間 | `HH:MM:SS+08:00` |
| commit | 短 SHA 7 碼；未提交 `NOT_COMMITTED` |
| SHA-256 | 全檔雜湊，記於 MANIFEST 與快照名 |
| 退役 | `DEPRECATED → RETIRED`；需 ADR、快照、redirect 表；不得刪除歷史 |

## 5. 各模組 README 模板

```markdown
# <模組繁中名>（<Module English Name>）
狀態：PROPOSED｜版本：<x.y.z>｜日期：<YYYY-MM-DD>｜Runtime：UNKNOWN

## 目的
## 範圍與非範圍
## 檔案
| 檔名 | 用途 | 版本 |
## 與其他模組的關係（上游／下游）
## 使用方式
## 驗收方式（AC 與檢查器）
## 失敗與回復
## 維護者與變更紀錄
## 未決事項
```

## 6. 熱插拔與 Runtime 宣告

見 LCV H-00～H-05；本文件不宣告任何 Runtime 能力。
