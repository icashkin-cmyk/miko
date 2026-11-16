# dghp-travel Source Atom Mapping Report

- mapping_method: `semantic_anchor_by_source_line_range; each source atom assigned to a candidate responsibility/step anchor`
- source_sha256: `22d0ecc87092eee1e3b496d0811bc3f813e236cdf9e0eec5a577c425879d01eb`
- candidate_sha256: `76f16de181900a2c3201446b199554af857cf2d72af471cb48bd0f039012fd0e`
- atom_count: `50`
- mapping_result: `PASS`

| ID | Source line | Source atom | Semantic candidate anchor | Status |
|---|---:|---|---|---|
| `TRAVEL-001` | 1 | --- | `0. 責任、資料、工具、輸出與授權` | `MAPPED` |
| `TRAVEL-002` | 2 | name: dghp-travel | `0. 責任、資料、工具、輸出與授權` | `MAPPED` |
| `TRAVEL-003` | 3 | description: 旅遊與行程規劃（一日遊、多日遊、跨縣市、交通與住宿整合）時使用：先依 USER_GOAL 分流，路線先行、閉環返程、官方班次與備案；含餐飲節點時交給 dghp-food。先載入 miko-core，再依本 Skill 的四段可執行步驟（天氣→地點與營業→班次→時間軸→判定）完成。純找吃的或單店研究不使用。 | `0. 責任、資料、工具、輸出與授權` | `MAPPED` |
| `TRAVEL-004` | 4 | --- | `0. 責任、資料、工具、輸出與授權` | `MAPPED` |
| `TRAVEL-005` | 6 | # dghp-travel v0.6｜旅遊行程規劃（Claude 版，可執行）｜2026-10-30 | `0. 責任、資料、工具、輸出與授權` | `MAPPED` |
| `TRAVEL-006` | 7 | 來源：Codex Skill dghp-travel-field-manual 1.1.0-CANDIDATE（治理整包快照）＋綜合區專案指令 §5–6＋MIKO 2026-10 指示。本 Skill 是 Claude 端精簡 Candidate，不宣稱等同原件；原件沒有、由 Claude 端加上的整合項標「（Claude 端整合）」。 | `0. 責任、資料、工具、輸出與授權` | `MAPPED` |
| `TRAVEL-007` | 8 | 載入順序：先 miko-core（四視角主流程、品質閘門），再本 Skill；以下依 miko-core §2.4 提供四段內容。v0.2 依 2026-10-26 實跑結果改寫（ADR-015）。 | `0. 責任、資料、工具、輸出與授權` | `MAPPED` |
| `TRAVEL-008` | 10 | ## 0. 分流（先做） | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-009` | 11 | - 純旅遊／排行程 → 本 Skill。純找吃的、單店研究 → 停止，改用 dghp-food。旅遊＋美食 → 本 Skill 主導，餐飲節點交 dghp-food。需求含糊（只說要去哪、沒說要吃還是要玩）時依意圖問一句，不強制轉美食。（2026-10-30，H-06） | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-010` | 12 | - 既有行程只換一餐 → 只重算該餐飲節點與前後路線、時間、成本，其他節點凍結；只有造成固定班次、最後入場、返程或重大預算的硬衝突才最小擴張。 | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-011` | 13 | - 有地名、位置或距離不等於要排行程。明顯是找吃的（提到餐點、餐廳、吃）→ FOOD；意圖看不出來 → 依上一條問一句，不預設為 FOOD。 | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-012` | 15 | ## 1. 問問題 | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-013` | 16 | - 必問（缺了才問，一次問完）：日期、起點、目的地或想去的點、最晚回到家的時間。 | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-014` | 17 | - 預設（沒說就用，並寫出採用的預設）：交通依使用者設定的交通方式（各種方式分開判斷，不預設使用者會開車或騎機車）；起點只給區名時用區公所當起點並標註；預算不限；寵物不同行。（Claude 端整合） | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-015` | 18 | - 對齊需求（原件 TR00、TR03）：時間、地點、交通方式、預算，以及使用者指定的硬性時間；寵物是否同行依原件 §10。 | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-016` | 20 | ## 2. 解決（可執行步驟） | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-017` | 21 | 規劃順序：起點與終點 → 主要交通 → 目的地樞紐 → 地理分群 → 景點／餐飲／休息 → 返程 → 終點。禁止無意義折返。 | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-018` | 22 | 1. 天氣（Claude 端整合：查詢時用 tw-alert-check）：T-7 看趨勢、T-24H 正式重驗、T-3H 當日重驗；體感 >32°C 啟用高溫路線，降雨機率 >60% 啟用雨天檢查；官方警報或封閉優先。32°C、60% 是規劃用的啟發值，不是官方危險標準；危險判斷依官方警報（tw-alert-check）。T-24H、T-3H 是做行程時的重驗點，不會自動新增排程。中央氣象署縣市頁是動態頁，網頁讀取工具可能讀不到數據（2026-10-26 實跑讀不到）：讀不到就標 NOT_RETRIEVED，附官方連結，判定最多到 NEEDS_FINAL_CHECK。 | `T1｜需求分流與最小資料` | `MAPPED` |
| `TRAVEL-019` | 23 | 2. 地點與營業：用 Google 地點搜尋（places_search）查每個點的地址、座標、每週營業時間；以目標日期的星期與預計抵達時間判斷常態開放與最後入場。週表不等於指定日一定開放：特別休館、臨時公告、最後入場或最後點餐要另查官方網站或官方社群公告，結果寫成「指定日狀態」；沒核到就標 UNKNOWN，該點會讓整體判定停在 NEEDS_FINAL_CHECK。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-020` | 24 |    - 名稱相近或分館要核對地址（實跑：查某景點的分館，回傳的是另一館，指定分館本體沒出現）；地址對不上就標 ENTITY_CONFLICT，不當已核實。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-021` | 25 | 3. 交通：班次必須對應目標日期；他日或一般時刻只能標 PROVISIONAL。官方來源優先（台鐵、高鐵、交通部 TDX；取得方式依當下工具實測，讀不到標 NOT_RETRIEVED，班次與票價一律不得生成）。固定班次、預約、最後入場、最後點餐建立 HARD_CUTOFF（抵達須早於最後入場或最後點餐）。不同交通方式要分開計算，並計入去程＋當地＋返程＋安全餘裕。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-022` | 26 |    - 騎車或步行時間：沒有導航工具時，用座標以程式算直線距離乘 1.3 估路程，再除以速度（使用者常用交通工具約 15 公里／小時（設定值）、步行約 4.5 公里／小時），一律標「估算，非導航」，判定最多到 NEEDS_FINAL_CHECK。（Claude 端整合） | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-023` | 27 | 4. 餐飲節點：交 dghp-food，順序是實體核驗 → 品質 → 路線適配 → 插入行程。本 Skill 只判斷路線、時間、距離、排隊、預算與閉環適配，不改寫 FOOD 的品質結論。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-024` | 28 | 5. 住宿（多日）：依當天最後一站與隔天第一站選區。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-025` | 29 | 6. 時間軸：每個節點寫抵達、停留、離開；最後一段必須回到起點，並和最晚回家時間比，留安全餘裕。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-026` | 30 | 7. 備案：用「條件 → 動作」寫，必須接回閉環；備用班次也要已核實。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-027` | 31 | 8. 呈現：用行程卡或地圖（itinerary_display、places_map_display）加文字；格式見 §5。地圖與行程卡只是呈現，不是核驗；平台沒有同名工具時改用文字表格，核驗與判定照常。 | `T2｜建立路線與天氣基線` | `MAPPED` |
| `TRAVEL-028` | 33 | ## 3. 後設（常見錯誤） | `T3｜核驗地點、營業與硬截止` | `MAPPED` |
| `TRAVEL-029` | 34 | 狀態不可混用：路線已規劃≠可執行；查到時刻表≠指定日期班次已核實；Google 找到實體≠本輪已取得 Google 資料核實；現在營業≠抵達時營業；找到旅館≠有空房；Google 星等≠目前餐飲品質；UNKNOWN≠PASS，成本 UNKNOWN 不得填 0。 | `T3｜核驗地點、營業與硬截止` | `MAPPED` |
| `TRAVEL-030` | 35 | - 景點：以目標日期與預計抵達時間判斷開放與最後入場。 | `T3｜核驗地點、營業與硬截止` | `MAPPED` |
| `TRAVEL-031` | 36 | - 分館、同名地點選錯；估算的騎車時間被當成導航時間；週末與平日營業時間不同。 | `T3｜核驗地點、營業與硬截止` | `MAPPED` |
| `TRAVEL-032` | 38 | ## 4. 檢查（驗收） | `T4｜計算交通、班次與時間軸` | `MAPPED` |
| `TRAVEL-033` | 39 | 執行判定：交通指定日、返程、景點指定日狀態、餐飲實體與抵達時營業及最後點餐、天氣、過夜住宿依適用性逐項驗。有 UNKNOWN → NEEDS_FINAL_CHECK；已知關鍵失敗（含已公告的指定日休館、停駛）或沒有返程 → DO_NOT_EXECUTE（可改排替代點後重驗）；必要項全部成立才是 READY_TO_GO。READY_TO_GO 只代表截至核驗時間的評估，要寫出核驗時間；出發前狀態有變就重驗。規格與呈現通過不等於旅程可執行。 | `T4｜計算交通、班次與時間軸` | `MAPPED` |
| `TRAVEL-034` | 40 | - AC-T1：時間軸閉環回到起點，且早於最晚回家時間。 | `T4｜計算交通、班次與時間軸` | `MAPPED` |
| `TRAVEL-035` | 41 | - AC-T2：每個點都有週表判斷與指定日狀態（特別休館、臨時公告、最後入場或點餐；沒核到標 UNKNOWN）。 | `T4｜計算交通、班次與時間軸` | `MAPPED` |
| `TRAVEL-036` | 42 | - AC-T3：天氣、班次標出官方來源或 NOT_RETRIEVED。 | `T4｜計算交通、班次與時間軸` | `MAPPED` |
| `TRAVEL-037` | 43 | - AC-T4：估算的移動時間標「估算，非導航」。 | `T5｜整合餐飲、住宿與備案` | `MAPPED` |
| `TRAVEL-038` | 44 | - AC-T5：給出 READY_TO_GO／NEEDS_FINAL_CHECK／DO_NOT_EXECUTE 判定、原因與核驗時間。 | `T5｜整合餐飲、住宿與備案` | `MAPPED` |
| `TRAVEL-039` | 45 | - 實跑題：「10/31（六）14:00 從住家出發，用常用交通方式去兩個市區景點，18:00 前回到家」→ AC-T1～T5 全過。2026-10-26 實跑：兩地週六都營業到 21:00；單程估算約 36 分鐘；排完約 17:40 到家；天氣 NOT_RETRIEVED、其中一個景點本體未直接核實、移動時間為估算，判定 NEEDS_FINAL_CHECK。 | `T5｜整合餐飲、住宿與備案` | `MAPPED` |
| `TRAVEL-040` | 47 | ## 5. 呈現 | `T5｜整合餐飲、住宿與備案` | `MAPPED` |
| `TRAVEL-041` | 48 | 摘要卡 → 時間軸 → 重要節點 → 備案 → 現場速查卡（現在／下一步、導航、移動與抵達、停留、硬截止、主／備班次、最小備案）→ 摺疊的來源。需要流程表時一律用 6 欄（ADR-004，取代原件 16 欄 ProcessStep16）：步驟／交付物、負責人、前置依賴、驗收條件、證據位置、狀態與下一步。 | `T5｜整合餐飲、住宿與備案` | `MAPPED` |
| `TRAVEL-042` | 50 | ## 6. 禁止 | `T6｜判定與交付` | `MAPPED` |
| `TRAVEL-043` | 51 | 直線距離冒充導航時間；他日班表冒充當日；Google 星等冒充品質；沒取得 Google 資料卻標已核實；UNKNOWN 當 0、False 或通過；捏造班次、票價、營業時間；沒有返程仍標可執行；只換一餐卻整個重排。寵物只在明確同行時才啟動同行檢查，並重驗當日狀態。 | `T6｜判定與交付` | `MAPPED` |
| `TRAVEL-044` | 53 | ## 7. 檢核程式（ADR-037，2026-11-04 併入） | `工具與程式要求` | `MAPPED` |
| `TRAVEL-045` | 54 | - 程式在本 Skill 的 scripts/：itinerary_check.py（行程檢核）、food_pool.py（美食候選池）、tests/（45 項）、README.md（輸入格式）。不連網、不需第三方套件。 | `工具與程式要求` | `MAPPED` |
| `TRAVEL-046` | 55 | - 取得（每個新對話第一次需要時做一次；下載或測試失敗就照本檔規則人工檢核並說明原因，不重寫程式）：`mkdir -p ft/tests ft/examples && cd ft && B=https://raw.githubusercontent.com/icashkin-cmyk/miko/main/skills/dghp-travel/scripts && for f in itinerary_check.py food_pool.py README.md tests/test_rules.py examples/範例_一日遊.json examples/範例_候選池.csv; do curl -sSLf -o "$f" "$B/$f"; done && python3 -I -B -m unittest discover -s tests`（45 項全過才使用） | `工具與程式要求` | `MAPPED` |
| `TRAVEL-047` | 56 | - 何時跑：行程定稿前，把行程寫成 JSON（格式見 README.md 與 examples/；README 是 v0.1 說明，v0.1.1 另加 trip.home、交通段 evidence.source_url／evidence.checked_at、access_min，以 tests/ 為準）→ `python3 -I itinerary_check.py 行程.json --out out`。 | `工具與程式要求` | `MAPPED` |
| `TRAVEL-048` | 57 | - 判定照程式輸出：EXECUTABLE（可執行）、有風險、INCOMPLETE_UNVERIFIED（未完整驗證）、NOT_EXECUTABLE（不可執行）。不得把程式的未驗證改寫成可執行；人工判斷與程式不同時兩個都寫並說明。 | `工具與程式要求` | `MAPPED` |
| `TRAVEL-049` | 58 | - 程式檢查：回程最後一段必須抵達 home；「已核班次」必須附官方網址與查核日期；每段大眾運輸預留進站、步行、購票、候車時間（未填預設 10 分鐘）與轉乘緩衝；營業時間與最後點餐。 | `工具與程式要求` | `MAPPED` |
| `TRAVEL-050` | 59 | - 尚未做（程式 README 列的 P2）：輸出表未顯示接駁、餐飲證據與最後一哩；TDX 取資料程式不在本版。 | `工具與程式要求` | `MAPPED` |
