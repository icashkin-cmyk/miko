未驗收提案

# Capability Inventory Schema

每筆能力至少包含：

| 欄位 | 要求 |
|---|---|
| capability_id | 穩定英文識別名 |
| display_name_zh_tw | 繁體中文名稱 |
| asset_type | skill／knowledge-card／adapter／workflow／reference／template／script／one-off |
| version | 版本；未知填 UNKNOWN |
| source | 來源位置、Commit、日期、License |
| purpose | 解決的問題 |
| triggers | 何時可觸發 |
| inputs | 輸入格式 |
| outputs | 輸出格式 |
| dependencies | Skill、工具、API、MCP、Runtime |
| permissions | 允許、禁止、需核准 |
| status | installed／callable／executable／verified／adopted／runtime_read_back，分欄記錄 |
| evidence | 測試命令、stdout、stderr、Exit Code、時間、SHA-256 |
| last_verified_at | 最後實際驗證時間 |
| limitations | 已知限制、UNKNOWN、BLOCKED |
| rollback | 回復方式 |
