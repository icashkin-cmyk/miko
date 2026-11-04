# Skills 公開版

這裡是 MIKO 各 Skill 的公開副本，給其他平台讀取與實測（原寫「給 Codex 等平台」；Codex 自 2026-11-02 停用，ADR-039）。已去除個人資料（寵物名、常用地區、交通習慣、本機路徑），完整版在 Claude 帳號；規則以根目錄 README.md（正本）為準，miko-core 開頭的「對應正本」版本號用來核對是否同步。

## 領域 Skill 採用狀態（ADR-050；miko-core §2.4 用）
「已採用」＝已推上本 repo main；「逐步閘門」依 miko-core §2.4 判定標準（每一步本行或縮排子項寫出輸入、輸出與閘門）。改動時只新增或改這張表的對應列，並在 CHANGELOG 記一筆。
| Skill | 版本 | 採用 | 逐步閘門 |
|---|---|---|---|
| dghp-beauty | v0.6 | 已採用 | 已補齊（正本 1.2.27） |
| dghp-food | v0.6 | 已採用 | 未核對（1.2.25 前採用，下次改「解決」節時補齊） |
| dghp-travel | v0.6 | 已採用 | 未核對（同上） |
| dghp-metaphysical-integrated-analysis | v0.2 | 已採用 | 未核對（同上） |
| gmail-cleanup | v0.3 | 已採用 | 未核對（同上；「解決」節為 §2 清理判定） |
| tw-alert-check | v0.2 | 已採用 | 未核對（同上；「解決」節為 §2 流程） |
| photo-inspection-log | v0.19 | 已採用 | 未核對（writer：照片專案） |
| tw-backtest-workflow | v1.8 | 已採用 | 未核對（writer：臺股專案） |
| safe-implementation | v0.2 | 已採用 | 未核對（通用 Skill，有可執行步驟，比照列出） |
