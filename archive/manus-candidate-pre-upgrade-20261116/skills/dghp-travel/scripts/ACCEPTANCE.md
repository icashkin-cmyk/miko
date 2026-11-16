# 驗收對照（2026-10-19，Python 3.13.16）

| 規則來源 | 檢查碼 | 測試 | 結果 |
|---|---|---|---|
| §3 必要輸入 | T00 | test_T00_missing_input_unknown | PASS |
| §3 不預設汽車／機車；微型電動二輪≠電輔車 | T01 | test_T01_car_without_license_fail／with_license_ok／micro_e2w_and_ebike_distinct_allowed／mode_not_allowed | PASS |
| §5 §7 回程優先、沒有可靠回程不出發 | T02 | test_T02_no_return_fail／return_unverified_unknown | PASS |
| §3 回家截止 | T03 | test_T03_home_deadline | PASS |
| 時序 | T04 | test_T04_time_order | PASS |
| §6 高風險轉乘不得稱穩健 | T05 | test_T05_short_transfer_risk | PASS |
| §3 一般班表≠指定日期開行 | T06 | test_T06_general_timetable_unknown | PASS |
| §5 跨日正規化（週五深夜 00:30＝週六） | D01 | test_D01_cross_midnight | PASS |
| §4 實體→品質→順路→排入 | F01 | test_F01_entity_not_verified_fail／order_skip_fail | PASS |
| §4 OPEN_NOW≠OPEN_AT_TARGET_ARRIVAL | F02 | test_F02_open_now_is_not_open_at_arrival | PASS |
| §5 ARRIVAL≠NODE_COMPLETION、L.O. | F03 | test_F03_arrival_ok_but_cannot_finish／last_order | PASS |
| §4 避免只有店名 | F04 | test_F04_name_only_risk | PASS |
| §6 使用者排除項持續排除 | X01 | test_X01_excluded_keyword | PASS |
| §7 UNKNOWN≠PASS | overall | test_T02_return_unverified_unknown 等 | PASS |
| FOOD 硬半徑（道路距離） | — | test_radius_is_hard／unknown_road_distance_pending | PASS |
| FOOD 核實後才排名 | — | test_unverified_entity_not_ranked／closed_excluded／open_now_not_target | PASS |
| FOOD 不湊數、五類分組、去重 | — | test_no_padding／categories_separate／bad_category_excluded／duplicate_store／ranking_order | PASS |
| FOOD 近期評論 0–180 日 | — | test_stale_review_not_qualified | PASS |
| 輸出檔產出 | — | test_markdown_and_csv_written／test_cli_outputs | PASS |

**單元測試**：33/33 OK。

**突變測試**（刻意破壞規則，確認測試會失敗）：8/8 被抓到——UNKNOWN 當 PASS、移除節點完成可行、移除跨日檢查、允許無照開車、不檢查回程、放寬半徑、湊數、OPEN_NOW 當目標時段。

**未驗證**：真實行程與真實店家資料的端到端使用（示範檔為虛構）；Router 原文與 FOOD M2 原文核對；外部 Reviewer 驗收（TRAVEL 8 題仍 AWAITING_EXTERNAL_REVIEW）。

---

# v0.1.1 修復驗收（2026-10-19，依外部偵錯報告 P0×2、P1×2）

| 報告項目 | 修法 | 新測試 | 結果 |
|---|---|---|---|
| P0 回程只到高鐵甲站仍 EXECUTABLE | `trip.home`（預設＝origin）；**實際最後一段交通**的 `to` 必須等於 home，不符 FAIL、未填 UNKNOWN | test_P0_return_stops_at_hsr_station_fail／last_leg_without_destination_unknown | PASS |
| P0 `date_specific_verified=true` 免證據 | 另需 `evidence.source_url`（https）＋`checked_at`，且網域屬官方清單（完整比對網域，擋仿冒網域）；否則 UNKNOWN | test_P0_verified_flag_without_evidence_not_pass／non_official_source_not_pass／lookalike_domain_rejected | PASS |
| P1 轉乘只比兩段交通時間差 | 每段大眾運輸上車前需 `access_min`（進站／步行／購票／候車，預設 10）；前一段也是交通時再加轉乘緩衝；景點→交通也檢查 | test_P1_access_time_spot_to_transit／access_default_applied | PASS |
| P1 FOOD 接受負距離、NaN 距離、NaN 評分 | 距離須為有限且 ≥0；分數須為有限且 0–100，否則 EXCLUDED | test_negative_distance／nan_distance／nan_score／score_out_of_range | PASS |
| 臺中高鐵一日遊（甲地⇄高鐵甲站⇄高鐵台中⇄市區）合成案例 | 完整閉環＋證據＋緩衝齊備才 EXECUTABLE | test_taichung_full_loop_executable | PASS |

**單元測試**：45/45 OK（原 33 項回歸＋新 12 項）。
**突變測試**：新規則 7/7 被抓到（不檢回到家、不要求證據、不檢官方網域、網域子字串比對、不算進站時間、不擋負數／NaN 距離、不擋異常分數）。
**未修**：P2 順向流程表缺真實接駁、餐飲證據與最後一哩的輸出呈現（不影響判定，下輪處理）。
**未驗證**：真實日期、真實官方班次的端到端資料（需台鐵資料來源開通或人工貼入官方查詢結果）。合成案例時刻非真實班次。
