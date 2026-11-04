---
name: "photo-inspection-log"
description: "施工查驗照片整理成公司格式「材料自主檢查照片」(Excel)：使用者在聊天室丟查驗白板照片就整理、更新；上傳上次的材料自主檢查照片.xlsx 就接續；回覆待確認的字就更新。版面依公司範本，名稱與品號依材料表（範本內的材料表分頁）。讀不清附放大圖問使用者。先載入 miko-core。"
---

# photo-inspection-log v0.17｜施工查驗照片整理（依公司範本）｜2026-11-04

## 一、整包取得（缺一不可）
本 Skill 必須整包使用，檔案一起下載，缺少範本就停止，不得自行排版。
- 必要檔案（GitHub icashkin-cmyk/miko 的 skills/photo-inspection-log/）：
  - scripts/材料自主檢查照片_範本.xlsx（範本分頁＋10 個材料表分頁，版面與名詞的唯一依據）
  - scripts/build_company.py（依範本版面產出 Excel）
  - scripts/make_entries.py（照片紀錄 → entries.json）
  - scripts/log_photo.py（白板照片讀取、抄寫、詞庫、回覆格式）
  - scripts/forms.csv（材料表名詞，給 log_photo.py terms 與詞庫用）
  - scripts/preflight.py（開工與交檔的防呆檢查）
- 下載（每個新對話執行一次，逐一下載，任一失敗就停止並告知使用者）：
  `mkdir -p work/scripts && cd work && B=https://raw.githubusercontent.com/icashkin-cmyk/miko/main/skills/photo-inspection-log/scripts && for f in log_photo.py build_company.py make_entries.py forms.csv preflight.py; do curl -sSLf -o scripts/$f $B/$f; done && curl -sSLf -o scripts/材料自主檢查照片_範本.xlsx "$B/材料自主檢查照片_範本.xlsx"`
- 下載失敗（網路被擋）：請使用者直接上傳整包 zip；不得只用其中一部分，也不得自行改寫程式。

## 一之二、防呆（一條龍，必須遵守）
- 開工第一步：`python3 scripts/preflight.py start`。任一項 FAIL 就停止，請使用者上傳整包 zip，不得開始處理照片。
- 交檔前：`python3 scripts/preflight.py deliver 材料自主檢查照片.xlsx entries.json`。任一項 FAIL 不得交檔。
- 不得使用 `log_photo.py export`（已停用，會回傳結束碼 7）。交付檔只能由 build_company.py 產生。
- 範本與材料表是唯一版面與名詞依據；範本中不得有公式（已清除，preflight 會檢查）。

## 二、流程
0. 開工：`python3 scripts/preflight.py start`（必須全部 PASS）。
1. 接續：使用者上傳上次的材料自主檢查照片.xlsx → `python3 scripts/log_photo.py restore 材料自主檢查照片.xlsx 照片紀錄.xlsx`。沒上傳 → 新建工作檔。
2. 收照片：`python3 scripts/log_photo.py prep incoming 照片紀錄.xlsx` → 抄寫白板（text/NNN.txt）→ `addmany`。
3. 產生 entries：`python3 scripts/make_entries.py 照片紀錄.xlsx entries.json photos_out`。
4. 填欄位（Claude 負責，依下列規則，寫入 entries.json）：
   - sec（分項工程名稱）：白板沒有；使用者給了就填，沒給就留空並在回覆問（一個查驗項目一題）。
   - item（檢查項目）：查驗項目去掉「材料進場」；能對到材料表就用材料表的「材料/設備名稱」。
   - design（設計/標準值）：對到材料表（範本內的材料表分頁）就用材料表的品質管理標準，第一行寫材料名稱；對不到就用白板規格，並在回覆列為「未建檔」。
   - measured（實測值）：白板有實測就照寫；白板沒有實測欄的，留空並在回覆說明（【待填】）。
   - shot / loc / bldg：照 make_entries.py 產生的值；棟別留空，由使用者提供。
5. 產出：`python3 scripts/build_company.py entries.json 材料自主檢查照片.xlsx`（版面複製自範本，每頁 3 筆，A4 直式）。
6. 檢查：用 LibreOffice 轉 PDF 抽看，照片在格內、文字沒有截斷；確認筆數＝entries 筆數、頁數＝ceil(筆數/3)。
7. 交檔：只交「材料自主檢查照片.xlsx」，有待確認時另交放大圖（`python3 scripts/log_photo.py crops ...`）。

## 三、回覆格式
- 每筆一段，格式：**日期｜第 N 筆**｜已新增。
- 查驗時間、照片日期照抄，然後「請確認」一題一行，附候選字（最多 3 個）。
- 分項工程名稱未填、未建檔物件、棟別未填、實測未填，各列一次。
- 新對話第一次交檔加一行：下次接續請上傳這次的材料自主檢查照片.xlsx。
- 不解釋判斷過程。

## 四、常見錯誤
- 沒有範本或材料表就開始排版：停止，請使用者上傳整包。
- 只下載部分檔案：流程會錯，必須整包。
- 白板品名與材料表寫法不同（例 鋁梯型直式 → 直式電纜線架）：用材料表的寫法，但在回覆說明對照來源。
- 材料表沒有的物件（衛生設備、遮煙捲簾、防煙垂壁、屋面防水）：照白板寫，列為未建檔，不套用近似品名。
- 手寫字看不清：附放大圖問使用者，不猜。
- 每個新對話用量：一批約 5 張，批次結束開新對話，用工作檔接續。不要求使用者縮圖。

## 五、檢查（驗收）
- AC-1 版面：輸出與範本同結構（每頁 46 列、標題、3 筆、頁碼）；照片在 A:E 格內；LibreOffice 轉 PDF 文字不截斷。
- AC-2 名稱：對到材料表的項目用材料表寫法；未對到的列在回覆。
- AC-3 筆數：輸出筆數＝entries.json 筆數＝工作檔資料列數。
- AC-4 缺件：範本、材料表、build_company.py、make_entries.py、log_photo.py、forms.csv 任一缺失則停止並說明。
- 實跑題：新對話上傳 1 張白板照片 → 整包下載 → 產出 材料自主檢查照片.xlsx，回覆格式符合第三節。

## 六、測試紀錄（2026-11-04）
- 整包從 GitHub 下載到乾淨資料夾後，preflight start 全部 PASS；build 2 頁、5 張照片；preflight deliver 全部 PASS。
- 缺檔時 preflight start 回報 FAIL 並停止。
- 範本與材料表合併為一個檔（範本分頁＋10 個材料表分頁），GitHub commit ea98eba。
- build_company.py 用 5 筆既有紀錄測試：2 頁，照片在格內；LibreOffice 版面與範本相同。
- 線槽「鋁梯型直式」對應材料表「鋁製電纜線架」：設計/標準值用材料表寫法。
- 分項工程名稱未填時顯示【待確認】（本機修正，尚未推 log_photo.py）。
