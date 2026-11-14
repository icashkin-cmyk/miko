---
name: miko-skill-format
name_en: MIKO Skill Format Writer
version: 1.0.0
owner_role: R-DESIGN
status: FINAL_CANDIDATE
trigger_keywords: [Skill 格式, 寫 Skill, skill 範本]
---

# miko-skill-format：合格 Skill 製作

## 一、問問題

**負責什麼**：依 Universal Skill Contract 產出一份合格的 Skill 檔，四節齊全、九項契約有落點、步驟表七欄完整。

**看哪些資料**：正本 miko-core 附檔 skill-format.md、USC 契約、既有的同類 Skill。

**接哪些連接器**：不需要。

**有沒有排程**：沒有。

**交回什麼**：`SKILL.md`，含 front matter、四節、P/C/J 七欄步驟表、實跑題。

**哪些先問 MIKO**：這個 Skill 負責什麼、要不要排程、哪些事要先問。

**觸發**：使用者說「寫 Skill」「Skill 格式」「做一個 Skill」。
**不觸發**：只是要一段規則文字。
**相近反例**：「這個任務怎麼做」是流程問題，不一定需要 Skill。

**邊界**：四節與七欄以 USC 為唯一來源；引用 UAC 時只取章節骨架與欄位名，不把元件、介面、資料流寫入 Skill 本體；Skill 的製作流程走 UCP A00～A13。

**硬禁止**：不得把兩個不相關的職責塞進同一個 Skill；不得省略失敗處理欄；不得用測試內容充當正文。

## 二、解決

| ID | 類型 | 觸發條件 | 操作要求 | 禁止事項 | 驗收證據 | 失敗處理 |
|---|---|---|---|---|---|---|
| S1 | C | 收到需求 | 確認單一職責、觸發詞、不觸發情境與反例 | 不得一個 Skill 管兩件事 | 職責一句話 | 職責不清標 `UNKNOWN` |
| S2 | P | 職責確認 | 寫 front matter 與四節骨架 | 不得缺節或改節名 | 四節標題 | 缺節回 S2 |
| S3 | J | 骨架完成 | 逐步填寫七欄，標 P／C／J，每步寫閘門 | 不得把判斷步標成程式步 | 七欄表 | 欄位不足標 `NOT_RUN` |
| S4 | C | 內容完成 | 跑 skill 檢查，確認四節、九契約、七欄 | 不得只看格式就說合格 | 檢查輸出 | 不合格回 S3 |

閘門：S1 沒有單一職責不得進 S2；S2 四節不齊不得進 S3；S4 檢查不過不得標已採用。

## 三、後設

常見錯誤是把「解決」節寫成願望清單而不是可執行步驟；把失敗處理寫成「再試一次」而沒有上限；把後設寫成優點介紹，沒有攻擊成果。

## 四、檢查

驗收條件：`AC-SF-01` 四節名稱與順序正確；`AC-SF-02` 九項契約都有落點；`AC-SF-03` 七欄齊全且類型正確；`AC-SF-04` 有一題實跑題與通過條件。

實跑題：用本 Skill 產出 miko-flowchart，通過條件是四個 AC 全過、檢查零缺欄。
