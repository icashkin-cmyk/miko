# DGHP 美食＋旅遊檢核工具 v0.1.1-CANDIDATE（2026-10-19）

狀態：本地 Candidate、NOT_INSTALLED、NOT_CANONICAL。未改任何原件、Skill、GitHub、Runtime。

## 這是什麼
把 `DGHP_TRAVEL_RULES.md`（2026-10-19，6567 bytes，SHA-256 `0269a842fb3eb47bf4f5adb21c726316f48832d77a17d94f3894a0ee234f0a62`）與 FOOD 承接規則中「可程式化」的部分做成兩支離線檢核程式。查班次、查營業、讀評論仍由人或 Claude 用網路完成；程式負責把結果填進表後，機械地擋下違規與未驗證項。

| 檔案 | 用途 |
|---|---|
| `itinerary_check.py` | 行程 JSON → 順向流程表 Markdown＋檢查 CSV，整體判定 EXECUTABLE／EXECUTABLE_WITH_RISK／INCOMPLETE_UNVERIFIED／NOT_EXECUTABLE |
| `food_pool.py` | 候選池 CSV → 五類分組、硬半徑、核實後才排名、不足不湊數的 Markdown＋判定 CSV |
| `examples/` | 虛構示範輸入（非真實店家或班次） |
| `tests/test_rules.py` | 45 項驗收測試 |
| `ACCEPTANCE.md` | 規則條號 ↔ 測試對照與驗收結果 |

## 用法（Python 3.10+，無第三方套件）
```
python3 itinerary_check.py examples/範例_一日遊.json --out out
python3 food_pool.py examples/範例_候選池.csv --radius-km 3 --top 3 --out out
python3 -m unittest discover -s tests -v
```

## 行程 JSON 欄位重點
- `trip`：`date`、`origin`、`home_deadline`（必要）；`modes_allowed` 預設 `walk/transit/ebike/micro_e2w`；`licensed_driver` 預設 false；`min_transfer_buffer_min` 預設 15（候選參數）；`exclude_keywords`。
- `steps[]`：`type` = transport／spot／food；時間 `HH:MM`，跨午夜寫 `00:30 +1` 或 `24:30`。
- 交通：`mode`、`date_specific_verified`、回程加 `is_return: true`。
- 餐飲：`entity_status`（GOOGLE_ENTITY_VERIFIED）、`food_review`、`route_fit`（DONE）、`open_at_arrival`、`last_order`、`wait_min`、`dine_min`、`signature`、`price`、`source_date`。

## 候選池 CSV 欄位
`name,branch,category,road_km,entity_status,business_status,open_at_target,quality_score,review_window,signature,price,source_date,search_angle`
`category` 限 正餐／小吃／甜點／飲品／伴手禮；`review_window` 限 0-30／31-90／91-180。

## 已知限制
- 不連網，不代查任何動態資訊；欄位空白一律 UNKNOWN。
- FOOD 品質細則（180D Freshness、Authentic Review 等）原文 `FOOD_DOCS_1.2.0_M2` 未取得，`quality_score` 由使用者／查詢者填，程式只檢查有無與時效區間。
- Router 原文未取得；跨日正規化與節點完成可行兩項依 TRAVEL_RULES §5 實作，待 Router 原文核對。
- 15 分鐘轉乘門檻、30／45 分鐘緩衝為候選參數，可在 `trip` 調整。
