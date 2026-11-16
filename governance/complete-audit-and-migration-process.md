# 完整轉移與合格審核流程

## 0. 狀態與放行總則

所有聲明必須分為：已確認、暫時假設、合理推論、未驗證、UNKNOWN、NOT_READ、NOT_RUN、BLOCKED。任何 AC 只能使用 `PASS`、`FAIL`、`NOT_RUN`、`NOT_READ`、`BLOCKED`、`UNKNOWN`。

`UNKNOWN`、`NOT_RUN`、`BLOCKED` 不得轉換成 `PASS`。未取得實際執行輸出、Exit Code、時間、版本與檔案路徑時，不得宣稱測試通過。

## 1. 站點順序

1. `S0_SCOPE_LOCK`：鎖定來源、目標、不可修改範圍與交付狀態。
2. `S1_SOURCE_READ`：讀取來源正文、附檔、references、scripts、tests；讀不到即 `NOT_READ`。
3. `S2_SOURCE_REGISTER`：保存 repo、branch、commit、版本、SHA-256、讀取範圍。
4. `S3_COPY_ISOLATE`：在 Manus 工作區建立原始封存副本與候選副本；原始來源唯讀。
5. `S4_CONTRACT_MAP`：依 Universal Skill Contract 建立責任、輸入、輸出、限制、失敗出口與證據欄位映射。
6. `S5_REWRITE`：只在候選副本重構；保留原始語意、例外、禁止事項與來源映射。
7. `S6_TEST_DESIGN`：建立正向、負向、邊界、異常、回歸、Mutation 測試。
8. `S7_IMPLEMENTER_SELF_TEST`：IMPLEMENTER 交付並保存自驗證據；不得自行宣稱獨立驗收。
9. `S8_TESTER_EXECUTION`：TESTER 自行讀取候選檔並執行測試，保存完整證據。
10. `S9_INDEPENDENT_AUDIT`：INDEPENDENT_AUDITOR 重新讀取版本、commit、檔案與測試，不接受前兩者 PASS 自述。
11. `S10_MUTATION_EFFECTIVENESS`：以錯誤注入證明測試真的能抓錯；Mutation 未被抓到時不得放行。
12. `S11_REGRESSION`：重跑原有通過案例、新增案例與跨 Skill 邊界案例。
13. `S12_REMOTE_RUNTIME`：若無遠端或 Runtime 實測，分別標 `NOT_RUN` 或 `UNKNOWN`，不得以本機結果代替。
14. `S13_GATE`：只有所有必要 AC 均 PASS，且沒有未處理 FAIL／NOT_RUN／BLOCKED／UNKNOWN，才可標 `QUALIFIED_CANDIDATE`。
15. `S14_ARCHIVE_HANDOFF`：保存 diff、證據、manifest、交接與回復方式，才可進下一筆。

## 2. 三角色分離

`IMPLEMENTER → TESTER → INDEPENDENT_AUDITOR` 是責任流，不是同一份 PASS 報告的改名。三者可以由同一平台的不同執行階段擔任，但每階段必須有不同執行證據、重新讀取目標與明確角色標籤。

- IMPLEMENTER：可以修改候選區，不得修改來源；負責產出與自驗。
- TESTER：不得只抄製作者輸出；必須自己執行必要測試。
- INDEPENDENT_AUDITOR：必須從候選檔重新讀取，重新核對 commit／版本／SHA-256，並保存與前兩者結果的差異。

## 3. 每項測試的強制證據欄位

`test_id`、`purpose`、`target_path`、`repository`、`branch`、`commit_sha`、`environment`、`command`、`stdout`、`stderr`、`exit_code`、`started_at`、`finished_at`、`result`、`role`、`evidence_path`。

沒有實際執行：`result=NOT_RUN`。只有預期輸出：不得填入 stdout。測試文件的預期結果不能當執行證據。

## 4. 測試有效性

每個可測試責任至少需要正向、負向、邊界、異常、回歸與 Mutation Testing。主動改壞規則、欄位、路由或輸出，測試必須失敗；抓不到 mutation 就是測試有效性 FAIL。

## 5. 反向測試優化

1. 建立來源原子項目清單：觸發、輸入、輸出、步驟、限制、禁止、例外、失敗出口、證據與版本。
2. 每個原子項目建立唯一 `source_atom_id`。
3. 候選文件每個規則、步驟與欄位至少回指一個 `source_atom_id`，或標記新增理由。
4. 每個來源原子項目必須被候選輸出覆蓋、明確移除理由，或標記 `NOT_READ`／`UNKNOWN`。
5. 檢查孤兒來源、孤兒輸出、責任越界、隱性新增、否定條款遺失、例外遺失、失敗出口遺失、狀態升格與證據欄位缺失。
6. 以 mutation 改壞一個原子項目，反向測試必須報告失敗。
7. 以雙向 coverage matrix 計算覆蓋率；分母由程式計算，不接受手填 PASS。

## 6. 放行條件

必要 AC 全部 `PASS`；三角色證據均存在；每項測試有完整執行欄位；Mutation 至少有一個預期缺陷且被捕捉；反向 coverage 無孤兒。遠端／Runtime 若屬適用範圍但未實測，不能標 Qualified，只能 `COMPLETE_WITH_CONCERNS` 或 `BLOCKED`。

## 7. 失敗與恢復

- FAIL：只修一個明確缺陷，保存 diff，重跑受影響測試與回歸。
- NOT_RUN：補足執行環境或明確保留未驗證，不得改寫成 PASS。
- NOT_READ：補讀指定來源；補不到則只停相依步驟。
- BLOCKED：保存阻塞原因、負責方、解除條件與可逆狀態。
- UNKNOWN：列出需要的證據，不自行推定。
- 連續兩輪無改善或達五輪上限：停止並交付失敗分析，不宣稱合格。
