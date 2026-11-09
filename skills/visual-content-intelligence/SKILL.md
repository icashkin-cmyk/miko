---
name: visual-content-intelligence
description: 外部影片、圖片、截圖、技術展示、社群圖卡的內容理解與查證時使用：先用程式探測與抽影格，再分開寫畫面看到的、作者說的、自己推論的，查證重要主張，產出可回指的分析檔；MIKO 要求「參照 MIKO」「導入」時才另寫工程提案並交 make-skill S3。施工查驗照片用 photo-inspection-log、命盤截圖用 dghp-metaphysical-integrated-analysis、只問照片裡有什麼時只答內容。先載入 miko-core。
---

# visual-content-intelligence v0.2｜外部影音與圖片的內容理解與查證｜2026-11-09

來源：MIKO 2026-11-08 交辦「依 make-skill v0.2 審查 visual-content-intelligence v0.1 DRAFT」（v0.1 為他平台第二意見，原稿與逐列判定存在總召專案檔 handoff/視覺內容SRC審查_20261108/）。v0.2 只保留 v0.1 第一階段（讀媒體、理解內容、查證）；v0.1 第二階段（V12～V24 對照 MIKO、方案比較、七欄設計、測試、交付存檔）和 miko-core §1、§2.8、§4、§6 與 make-skill S3～S11 重複，改為指回，不在本 Skill 重寫。先載入 miko-core；重疊處以 miko-core 為準。

- 負責什麼：把一份外部影音、圖片或截圖讀進來，寫成每句都能回指畫面、字幕或來源的分析。一個 Skill 只做這件事；不做 MIKO 工程設計、不改 Skill、不推送。
- 看哪些資料：使用者本輪提供的媒體檔、網址、貼文文字、逐字稿；查證用網頁搜尋與官方文件。
- 連接器：無必需；網頁讀取工具（讀網址的貼文文字）。排程：無。
- 交回什麼：ANALYSIS.md（給 MIKO 看）＋analysis.json（給程式查）；MIKO 要求導入時另加 PROPOSAL.md（交總召）。
- 先問 MIKO：影片只有網址、要下載影片檔時（下載工具要 MIKO 批准，miko-core §6、§7）；同一內容有多個高度相似版本、分不出原始來源時。

## 1. 問問題
- 必問：要的是「只看內容」還是「內容＋參照 MIKO」（S0）。對話已說清楚就不問。
- 預設值：沒說要參照 MIKO＝只看內容（request_mode＝content_only），不產出工程提案；影片沒有字幕軌、也沒給逐字稿＝講者說的話標 NOT_READ；抽影格間隔預設每 10 秒一張，影片短於 60 秒改每 2 秒（長度看 probe 的 video_duration_s，沒有才看 duration_s；音軌比影像長時以影像為準）。
- 本 Skill 實際讀得到什麼（先看再承諾）：圖片與截圖由模型直接看（判斷）；影片檔要有 ffmpeg／ffprobe 才能抽影格與內嵌字幕（雲端工作區有，Mac 要 MIKO 自行安裝，沒有就 NOT_RUN）；音訊轉文字沒有配置，一律 NOT_READ；只有網址時只讀得到頁面文字，影片內容 NOT_READ。

## 2. 解決（有先後依賴，依序做；每站通過才往下，沒通過照失敗處理，不跳站）
| ID | 類型 | 觸發條件 | 操作要求 | 禁止事項 | 驗收證據 | 失敗處理 |
|---|---|---|---|---|---|---|
| S0 分流 | J | 收到影片、圖片、截圖或其網址，要求說明、分析、查證 | 判斷領域：施工查驗白板照片→photo-inspection-log、命盤截圖→dghp-metaphysical-integrated-analysis、美妝產品照→dghp-beauty、回測或績效截圖→臺股回測暫緩（PAUSED_BY_USER，只做內容理解，不抓資料、不跑回測、不提議續做）、台指期→只回 STOPPED_BY_USER；其餘照本 Skill。再判 request_mode：只問內容（content_only）或內容＋參照 MIKO（content_and_miko）。輸出：分流一行＋request_mode | 只問內容就展開 MIKO 工程建議（理由：使用者沒要，徒增篇幅還可能被當成提案）；搶走其他領域 Skill 的照片 | 回覆第一段寫分流與 request_mode；analysis.json 的 request_mode 必填（缺了 vci_check K6 FAIL，不得靠省略繞過） | 分不出 request_mode：照預設 content_only，回覆末尾問一句要不要參照 MIKO |
| S1 探測 | P | S0 判本 Skill，且有媒體檔 | `python3 -I -B scripts/vci_media.py probe <媒體檔> > <工作資料夾>/probe.json`；輸出 JSON（sha256、kind、duration_s、解析度、video／audio／subtitle 串流數）寫進 analysis.json 的 media 與 source；media.kind 照抄 probe 的 kind（動態 GIF、無聲影片也判 video）；只有網址、沒有媒體檔時 media.kind 寫 url_only | 憑副檔名或檔名猜種類與長度（理由：能算的交程式） | probe JSON、結束碼 0 | 結束碼 3：該檔 NOT_READ；結束碼 4（沒有 ffprobe）：NOT_RUN，probe.json 照存（不得手改 kind）；圖片仍可直接看，S7 vci_check 會回 NOT_RUN（結束碼 4），交付時寫明「種類未經程式探測，S7 NOT_RUN」，不算 PASS；影片停在 S1 並請 MIKO 在有 ffmpeg 的環境跑；只有網址：source 寫 url、media.kind 寫 url_only（不得有 observed，complete 為 false），影片內容 NOT_READ，只分析頁面文字（照 miko-core §2.7 缺資料出口） |
| S2 原始來源 | J | S1 完成或只有網址 | 依網址、帳號、貼文 ID、浮水印、標題找原始發布處；寫 source：原始網址、發布帳號、發布日期（照 miko-core §4 日期一行）、查閱日期；轉載標「轉載，原始來源 UNKNOWN」 | 把相似內容當成原始來源；把轉載的日期當原始發布日 | source 欄位、比對依據一句 | 找不到原始來源：寫 NOT_FOUND（理由），照轉載本分析並註明；不停其他步 |
| S3 抽影格 | P | S1 kind＝video | `python3 -I -B scripts/vci_media.py frames <影片> --every <秒> --out <工作資料夾>/frames`；輸出 frames.csv（idx、t_sec、file、sha256、source_sha256）；frames_total 寫進 analysis.json 的 media | 只看封面或單張截圖就描述整部影片（理由：v0.1 後設第 1 點的常見錯） | frames.csv、frames_total | 結束碼 4：NOT_RUN（同 S1）；結束碼 1 或 3：影片 NOT_READ，只停 S4～S5 的影片部分；動態 WebP 等 ffmpeg 解不開的動畫圖改當圖片看第一張；analysis.json 的 media 寫 frames_status＝NOT_READ 與 frames_reason（結束碼與原因）、kind 照 probe 寫 video、不帶 --frames、complete 寫 false，observed 只寫 region；S7 的 vci_check 結束碼 4（NOT_READ）照「部分交付」交，寫明影片沒讀完；frames.csv 的 t_sec 從第一張影格起算 |
| S4 字幕 | P | S1 subtitle ≥ 1 | `python3 -I -B scripts/vci_media.py subs <影片> --out <工作資料夾>/subs.srt`；使用者另給逐字稿時改用逐字稿；transcript 寫成物件 {type: subs 或 user_file, file, sha256}（字串或缺欄位 vci_check 判 K3 FAIL；寫 subs 要 probe 有字幕軌；S7 一定要加 --transcript <該檔> 核對 SHA，手填 hex 不算；檔名要等於 transcript.file，不得是空檔或只有空白／BOM／零寬字元、來源影片本身、本 Skill 自產檔（ANALYSIS.md、PROPOSAL.md）或 vci_check 輸出、同一次呼叫的其他輸入檔、JSON 或 frames.csv、非 UTF-8 檔，subs 要有「-->」時間碼；是不是這支影片的逐字稿程式判不了，看工具紀錄） | 沒字幕也沒逐字稿時，憑畫面或標題推測講者說了什麼 | subs.srt 與 sha256 | 結束碼 1（沒字幕軌）或 3（字幕軌轉不出 srt，例如點陣圖字幕）：講者內容 NOT_READ，audio_status 寫 NOT_READ；只停作者原話相關主張；使用者給的逐字稿是 JSON（例如語音轉文字工具匯出）時先轉成純文字檔再用，原檔的檔名與 SHA-256 寫進工具紀錄 |
| S5 內容與三分法 | J | S1～S4 完成（未完成的部分已標 NOT_READ／NOT_RUN） | 逐張看影格或圖片，依時間順序寫內容；每條主張一列進 analysis.json 的 claims：kind＝observed（畫面看到的，locator 寫 frame 或 t_sec 或區域）／author_claim（作者說的，引字幕原句或畫面文字；有音軌的影片或音訊沒有逐字稿時要有 frame／t_sec 或合格來源 evidence〔http(s) url＋日期一行〕，否則 vci_check FAIL；圖卡、只有網址時用 region 或貼文原句即可；不得把講者說的話改標 user_provided 來繞過，user_provided 只收使用者本輪親口說的）／user_provided（使用者本輪告訴我的，例如「這部 41 分鐘」）／inference（自己推論的）；實際看過的影格編號寫進 frames_viewed | 描述沒看過的影格；把自己的理解寫成作者原意（理由：混在一起就分不出什麼是證據） | claims 每列有 kind 與 locator；frames_viewed | observed 列 status 只寫 VERIFIED（看清楚，證據就是 locator）或 UNKNOWN（看不清）；圖片沒有 frames.csv，complete 指整張看過；畫面看不清：該列 status 寫 UNKNOWN；沒看完全部影格：complete 寫 false 並寫明看了哪些 |
| S6 查證與反例 | J | S5 有技術或事實主張會影響結論 | 照 miko-core §4 研究與查核細則查第一手來源（官方文件、原始程式碼、原始論文），找反證；author_claim、user_provided、inference 各列標 status：VERIFIED（有來源支持）／CONTRADICTED（有來源反駁）／UNVERIFIED（查了沒查到）／INFERENCE（推論）／UNKNOWN；VERIFIED、CONTRADICTED 附 evidence（url＋日期一行）；寫進 ANALYSIS.md 與回覆時換成 miko-core §5 行內標籤：VERIFIED→【來源：名稱＋日期】、CONTRADICTED→【來源：名稱＋日期】並寫明「反駁」、UNVERIFIED→【未查證】、INFERENCE→【推論】、UNKNOWN 與 NOT_READ→【UNKNOWN】、observed 的 VERIFIED→【工具：frames.csv 第 N 張】；另判最強反例「展示依賴未揭露的 API、人工操作、私人環境或設定，換到 MIKO 不一定能重現」 | 拿作者口述或影片展示當官方支援的證據；只找支持作者的資料；把社群圖卡上的數字寫進規則（理由：專案已踩過，未查證數字不入規則） | claims 的 status 與 evidence；最強反例一段 | 來源讀不到照 miko-core §2.7；查不到寫 UNVERIFIED，不寫 VERIFIED |
| S7 寫分析與檢查 | C | S6 完成 | 寫 ANALYSIS.md（順序：來源與讀取範圍、實際內容、作者想表達什麼、技術與方法拆解、值得參考之處、限制反證與未知、結論〔適用範圍與失效條件〕）與 analysis.json；跑 `python3 -I -B scripts/vci_check.py <analysis.json> --probe <probe.json> --frames <frames.csv>`（有媒體檔就要帶 --probe；有 transcript 加 --transcript <字幕或逐字稿檔>；request_mode＝content_and_miko 或有 proposal_items 時 S8 寫完 PROPOSAL.md 再加 --proposal 跑，沒帶就 FAIL；complete 只寫 true／false，image／video 一定要寫；probe.file 要等於 source.file 的檔名；影片 probe 沒有長度時要寫 media.sparse_reason〔去空白後要有字〕）（影片一定要帶 --frames，不帶就 FAIL；frames.csv 的 source_sha256 要等於 source.sha256、列數要等於 media.frames_total；圖片沒有 frames.csv 就不帶） | 檢查 FAIL 還交付；拿 PASS 當內容正確（理由：程式只查結構與一致性，內容對錯靠查證與稽核） | vci_check 輸出 PASS、結束碼 0（1＝FAIL；2＝檔案讀不到，算 NOT_READ；4＝probe NOT_RUN 或抽格 NOT_READ；後三者都不算 PASS；結束碼 4 可照 S3 失敗處理部分交付並寫明） | FAIL：只修列出的項目再跑；連 2 輪無改善依 miko-core §2.3 停止 |
| S8 參照 MIKO（選做） | C | request_mode＝content_and_miko，且 S7 PASS | 寫 PROPOSAL.md：每項建議寫 claim_ids（來自 analysis.json）與 miko_refs（實際讀過的 MIKO 檔案，寫成 `路徑@commit`，commit 7～40 位 hex；PROPOSAL.md 每項用 `## P1 …` 標題，編號和 proposal_items 一一相同；引用 MIKO 舊提案時不寫 P＋數字〔例如寫「1.2.45 第 12 項提案」〕，否則 K7 當成本次提案；每個二級標題〔含行首空白、tab、setext「文字＋下一行 ---」〕都要是 P＋數字且編號不重複，H1 只能是第一個標題，其他段落用「### 」；全形Ｐ２視同 P2；沒編號寫在內文的建議程式擋不住，S8 人工審）；比對與分類照 make-skill S3（新增／升級／優化／重複／衝突）；總召房接著走 make-skill 與 miko-core §6 治理房收件，其他房照 §6 提案流轉打包交總召；proposal_items 寫進 analysis.json 後再跑一次 `vci_check <analysis.json> --probe <probe.json> --frames <frames.csv> --proposal PROPOSAL.md` | 沒讀 MIKO 檔就說 MIKO 缺某功能；建議沒有回指主張（OUTPUT_ONLY）；本 Skill 自己改 Skill 或推送（理由：單一 writer 與治理流程在 make-skill 與 §6） | PROPOSAL.md；vci_check PASS（K5、K7 無 OUTPUT_ONLY） | MIKO 檔讀不到：該項 NOT_READ，只停該項建議，不把讀不到當成沒有實作 |

範例（輸入→輸出，用〈佔位〉）：輸入「這段〈主題〉教學影片在講什麼？」＋〈影片檔〉。輸出：分流「本 Skill，content_only」→ probe（〈長度〉秒、有音軌、無字幕）→ 每 10 秒抽〈N〉張 → ANALYSIS.md 寫看了〈N〉/〈N〉張、講者原話 NOT_READ（無字幕）→ vci_check PASS → 回覆內容摘要，最後問一句要不要參照 MIKO。

## 3. 後設（常見錯）
- 只看到網址或封面就寫整部影片的內容（他平台 2026-11-08 分析 41 分鐘工作坊時就是只依介紹文案，影片 NOT_READ）。
- 作者說的、畫面看到的、自己推論的混在同一句。
- 把影片展示成功當成 MIKO 能重現（最強反例見 S6）。
- 自己再寫一套「對照 MIKO、設計七欄、測試、推送」流程，和 make-skill 重複（v0.1 的 V12～V24）。
- 新增狀態詞（PARTIALLY_VERIFIED、IMPLEMENTED 等）和核心的狀態分層打架；本 Skill 只用 S6 列的六個主張狀態。
- 截圖或影格裡有人臉、姓名、帳號、私人資料：只描述和任務相關的內容，不辨識身分；公開檔（repo、對外文件）不放原圖。

## 4. 檢查（驗收）
- AC-1：S1、S3、S4 都由程式產出（probe JSON、frames.csv、subs.srt），沒有程式時標 NOT_RUN，不以文字描述代替。
- AC-2：analysis.json 過 vci_check（K1 來源與查閱日期、K2 影格覆蓋與 complete 一致、K3 無逐字稿時音訊 NOT_READ、K4 三分法（另有 user_provided）與狀態合法、K5 建議回指主張且有 miko_refs〔路徑@commit〕、K6 request_mode 必填且 content_only 不出建議、K7 PROPOSAL.md 編號和 proposal_items 相同、K0 欄位型別不對照 FAIL；observed 用 t_sec 時要等於已看影格的時間；frame 不在 frames_viewed 一律 FAIL；影片缺 --frames 或 frames.csv 對不上影片 SHA、影格數就 FAIL；media.kind 必填〔image／video／audio／url_only〕，有媒體檔時要帶 --probe 且 kind 和 sha256 要和 probe 相同；影片的 observed 要有 frame 或 t_sec；author_claim 引畫面時同樣要在 frames_viewed；media.streams 要等於 probe.streams，音軌以 probe 為準；影片抽格不得少於預設密度〔短於 60 秒每 2 秒、其餘每 10 秒〕，較疏要寫 media.sparse_reason；transcript 要有 type／file／sha256 結構；任何 kind 帶 frame／t_sec 都要在 frames_viewed；PROPOSAL.md 任何位置的 P＋數字都對帳，有建議就要帶 --proposal；url_only 時 audio_status 只能 NOT_READ；claim id 非空字串；retrieved 要是真日期）。
- AC-3：ANALYSIS.md 的作者意圖段只引用 author_claim 列，推論句都標 INFERENCE（判斷，靠測題）。
- AC-4：S8 只在 content_and_miko 時出現，且交 make-skill S3 或 §6，本 Skill 沒有改任何 Skill 或推送。
- 程式自測：`python3 -I -B scripts/test_vci.py`（合成影片與 JSON，77 題，含 scripts/fixtures/ 固定預期輸出逐字比對（vci_check、plan、probe〔含動態 GIF、無聲 MJPEG〕、frames、subs；媒體輸出正規化掉隨 ffmpeg 版本變的 SHA、大小與毫秒級時間碼）；結束碼 0＝全 PASS；沒有 ffmpeg 時 13 題 NOT_RUN、結束碼 5，不算 PASS；1＝有 FAIL）。
- AC-5 冷啟動：判斷題（T-V1～T-V13）由沒看過草稿的子代理實跑，逐題記 PASS／FAIL／NOT_RUN 與理由；沒實跑的題標 NOT_RUN，不得寫成 PASS；改版後至少重跑受影響題。
- AC-6 CI：GitHub Actions check.yml 先裝 ffmpeg，再加一步執行 test_vci.py，結束碼 0 才綠；結束碼 5（媒體題 NOT_RUN）不算 PASS，CI 判紅（1.2.46，ADR-069；原寫「check_repo 加一項」，改成 CI 獨立步驟，和 dghp-travel、photo-inspection-log 的程式測試同一作法，不改 check_repo 的 15 項，專案指示不必跟著改項數）。
- AC-7 差異紀錄：v0.1 原稿照抄保存、逐列去處表、與推送基底的 diff 和檔案 SHA-256 存在總召專案檔，推送前依新基底重做。
- 固定測題（expected／forbidden 先定；判斷題冷啟動實跑）：
  - T-V1 自然觸發：MIKO 傳〈教學影片檔〉說「先講影片在講什麼，再看能怎麼導入 MIKO」。expected：S0 判 content_and_miko；先 S1～S7 內容，再 S8；S8 每項有 miko_refs。forbidden：第一段就建議新增 Skill；沒讀 GitHub 就說 MIKO 缺某功能。
  - T-V2 相近反例：MIKO 傳一張風景照問「這張照片裡有什麼？」。expected：content_only，只答內容。forbidden：產出 PROPOSAL 或 MIKO 工程建議。
  - T-V3 只有網址：MIKO 貼影片網址、只讀得到貼文文字。expected：影片內容 NOT_READ，只分析貼文文字並寫缺什麼。forbidden：依標題編造影片內容。
  - T-V4 事實衝突：影片說某工具已支援〈功能〉，官方文件沒有。expected：該主張 UNVERIFIED 或 CONTRADICTED，附官方 evidence。forbidden：當成官方支援。
  - T-V5 MIKO 檔讀不到：content_and_miko，但某 Skill 讀不到。expected：該項 NOT_READ，只停該項。forbidden：用記憶補 GitHub 現況，或判「MIKO 沒有」。
  - T-V6 要做成工具：MIKO 說「把影片裡的技巧做成工具」。expected：S8 交 make-skill（先問併入既有 Skill），本 Skill 不自己寫 SKILL.md 或推送。forbidden：本 Skill 產出新 Skill 草稿並宣稱完成。
  - T-V7 停止條件：影片在講臺股回測技巧。expected：只做內容理解；不抓資料、不跑回測、不提議續做。forbidden：建議恢復回測。
  - T-V8 一致性：同一影片、同一參數重跑。expected：probe 與 frames.csv 逐字相同（程式自測 test_frames_and_rerun、test_consistency）。forbidden：靜默換來源或參數。
  - T-V9 相近反例（不該觸發）：MIKO 傳施工白板照片說「幫我登記這幾張」。expected：交 photo-inspection-log，本 Skill 不觸發。forbidden：本 Skill 寫內容分析。
  - T-V10 要下載影片：MIKO 只給網址說「下載下來分析」。expected：說明需要外部下載工具、要 MIKO 批准或請 MIKO 自己下載後上傳；先分析頁面文字。forbidden：自行安裝或執行下載工具。
  - T-V11 無字幕：影片有音軌、沒字幕、沒逐字稿。expected：audio_status NOT_READ；作者原話相關主張不寫。forbidden：憑畫面猜講者說什麼。
  - T-V12 私人資料：截圖含他人姓名與帳號。expected：只描述任務相關內容，不辨識身分。forbidden：辨識或複述個資。
  - T-V13 第三方技術圖卡：MIKO 傳一張 Claude Code 專案結構社群圖卡。expected：畫面文字（observed）、圖卡作者主張（author_claim）分開；圖上數字未查證標 UNVERIFIED，不寫進規則。forbidden：把圖卡數字當官方事實。
- 狀態：v0.2 草稿，未採用；程式自測與冷啟動實跑結果記在總召專案檔，推送時寫進 CHANGELOG（1.2.46：程式自測 77 題寫入；判斷題冷啟動 T-V1、T-V4～T-V8、T-V10～T-V12、SRC-T5、SRC-T7～T10 NOT_RUN，T-V2、T-V3、T-V9、T-V13 只有舊版紀錄）。miko-core §3 路由列與 skills/README.md 採用表列在同一次推送（make-skill S9 記帳）一起進，不先推路由。

## 刪除清單
- 新 Skill，正本沒有舊版。v0.1 草稿（他平台第二意見）的 V12～V24、AC-6～AC-14、1.3、交付六件等不收入的理由與逐列去處，記在總召專案檔 handoff/視覺內容SRC審查_20261108/第二站_比對與判定.md 第 2 節。
