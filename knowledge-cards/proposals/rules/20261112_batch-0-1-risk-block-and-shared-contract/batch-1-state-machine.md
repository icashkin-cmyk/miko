# 未驗收提案

## 批次 1 共用狀態機候選
### 0. 狀態軸分離（候選修訂）

共用契約把狀態拆成四個互不替代的軸：

| 軸 | 允許值 | 說明 |
|---|---|---|
| 來源 | `NOT_READ`／`READ`／`PARTIAL_READ`／`CONFLICT`／`UNKNOWN` | 來源與來源讀取證據；不表示步驟已執行 |
| 執行 | `NOT_RUN`／`RUNNING`／`PASS`／`FAIL`／`PARTIAL` | 本步驟實際執行結果；不表示已獲授權 |
| 授權 | `NOT_REQUESTED`／`UNKNOWN`／`APPROVED`／`REJECTED`／`EXPIRED` | 當次精確批准狀態；不得用 PASS 或 BLOCKED 代替 |
| 範圍 | `CANDIDATE_ONLY`／`READ_ONLY`／`EXTERNAL_WRITE`／`FORMAL_RUNTIME` | 產物／操作可及範圍；候選預設不得進入正式 Runtime |

`PAUSED_BY_USER` 是 `route.mode` 的停止路由，不屬於來源、執行、授權或證據狀態；只能由 MIKO 明確撤銷同一停止後離開。四個軸與任務四態也不能互相推導或替代。


本文件是 `knowledge-cards/proposals/rules/20261112_batch-0-1-risk-block-and-shared-contract/` 的候選規則，尚未寫入 `miko-core`、任何 Skill 正本或正式路由。

### 1. 證據狀態

| 狀態 | 意義 | 可否繼續 | 不可做的事 |
|---|---|---|---|
| `NOT_READ` | 指定來源存在或應存在，但本輪讀不到 | 只可繼續不依賴該來源的步驟 | 不可把來源內容當已讀，不可用舊副本解除 |
| `NOT_RUN` | 應執行的步驟尚未執行 | 只可執行該步驟或獨立步驟 | 不可當成 `UNKNOWN`，更不可當 `PASS` |
| `UNKNOWN` | 已嘗試，但證據不足以判定 | 可保留已完成的獨立結果 | 不可升格完成、不可補猜 |
| `CONFLICT` | 兩份來源、版本、輸入或讀回結果互斥 | 停止受影響相依步驟 | 不可自行選較新或較方便的一方 |
| `BLOCKED` | 缺資料、決定、授權、付費或不可逆閘門 | 停在可逆狀態，等待解除條件 | 不可繞過授權、換路徑掩蓋阻塞 |
| `PARTIAL` | 多個子步驟中只有部分完成 | 可交付獨立子結果並列出缺口 | 不可包裝成全案成功 |
| `PASS` | 單一檢查或單一步驟的驗收條件通過 | 可進入已通過步驟的相依站 | 不等於任務完成、採用或 Runtime 生效 |

### 2. 任務四態聚合

| 任務四態 | 必要條件 |
|---|---|
| 完成 | 所有適用 AC 有證據、相依步驟 PASS、沒有關鍵 UNKNOWN／CONFLICT／NOT_RUN／BLOCKED／PARTIAL，且路由已獲採用授權 |
| 完成但有疑慮 | 技術 AC 可判定，但仍有非關鍵 UNKNOWN、殘留風險或等待 independent audit／治理裁決 |
| 需要資料 | 缺來源、缺讀回、缺資料、缺授權或缺決策，且存在可明確描述的解除條件 |
| 卡住 | 連續兩輪無改善、沒有可用替代來源、不可逆閘門未解除或無法安全繼續 |

`PARTIAL` 是證據狀態，不是任務四態；它通常聚合為「完成但有疑慮」或「需要資料」，不可直接聚合為「完成」。

### 3. 狀態轉移

```text
NOT_RUN
  ├─ 執行前置條件不足 → BLOCKED
  ├─ 來源不可讀 → NOT_READ
  ├─ 工具已執行但證據不足 → UNKNOWN
  ├─ 同一輸入／來源互斥 → CONFLICT
  ├─ 子步驟部分完成 → PARTIAL
  └─ AC 與證據全數通過 → PASS

NOT_READ / UNKNOWN / CONFLICT / BLOCKED / PARTIAL
  ├─ 新證據解除且重新驗收 → PASS 或 PARTIAL
  ├─ 新證據仍不足 → 原狀態維持
  └─ 依賴關係受阻 → 相依步驟 NOT_RUN 或 BLOCKED

PAUSED_BY_USER
  ├─ 只有 MIKO 明確撤銷同一停止才可離開
  └─ 「繼續」、再次點名或 force 不得解除
```

### 4. 共用不變量

1. `adopted=false` 時，路由不得是 `ADOPTED` 或 `EFFECTIVE`。
2. `read_only=true` 時，`external_write` 必須為 `false`。
3. `PAUSED_BY_USER` 優先於一般路由與「繼續」指令。
4. `NOT_RUN` 不得被轉成 `UNKNOWN` 或 `PASS`。
5. `UNKNOWN` 不得被補猜成 PASS。
6. `CONFLICT` 不得由代理自行裁決。
7. `BLOCKED` 不得以替代命令、force、無限重試或改 URL 繞過。
8. `PARTIAL` 不得聚合成全案完成。
9. 本機寫入成功不等於遠端發布；遠端回應成功不等於讀回驗證成功。
10. 技術 PASS 不等於正式採用、治理放行或 Runtime 生效。
11. 每個外部或副作用操作必須有唯一 `operation_id`；同一 ID 重跑只能先讀狀態，不得盲目重送。
12. 任一相依步驟的證據狀態不足時，只停止受影響的相依步驟，不得抹掉已完成的獨立結果。

### 5. 失敗類別與出口

| 類別 | 固定出口 |
|---|---|
| 缺資料 | 指定一個權威不低於原來源的替代來源試一次；仍取不到標 `NOT_READ`，列受影響相依步驟 |
| 缺決定／授權／付費 | `BLOCKED`；明列 MIKO 必須完成的精確一步；不得改找來源繞過 |
| 技術失敗 | 回到失敗的上一個可重現步驟；下一輪只修一個目標；連續兩輪無改善則「卡住」 |
| 外部依賴 | 列負責方、證據、解除條件；不把提醒當解除，不把未回覆當批准 |

### 6. 最小操作生命週期

```text
建立 task_id
→ 建立 operation_id
→ 檢查 route gate
→ 檢查 input／source pin
→ 執行單一步驟
→ 記錄 stdout／stderr／exit code
→ 原子保存候選產物
→ 讀回並核對 SHA-256
→ 更新 step status
→ 聚合 task_state
→ 產生交接索引
```

如果在「讀回並核對 SHA-256」失敗，產物不得標 `committed=true`；任務只能是 `UNKNOWN`、`CONFLICT` 或 `BLOCKED`。

### 7. 批次 0 與批次 1 的關係

批次 0 先限制「能不能做」；批次 1 再定義「做了之後如何記錄與判定」。批次 1 不得用 schema 反過來解除批次 0 的任何封鎖。

## 本提案狀態

- 狀態：`PROPOSED`
- 採用：`NOT_ADOPTED`
- 正式路由：未修改
- 正本：未修改
- 測試：尚未連接正式 CI
- independent audit：`NOT_RUN`
- MIKO 治理裁決：`NOT_REQUESTED`
