未驗收提案

# Stage 3｜Concept-to-Capability 概念萃取與能力轉化

- 目的：將一句話、零散想法、語音、圖片、文件或網址轉成可研究、可驗證、可實作的能力需求。
- 輸入：原始概念、目標、素材、限制、Stage 1 能力目錄與 Stage 2 分類規則。
- 輸出：Concept Record、問題拆解、目標成果、候選能力、缺口、驗收條件與權限需求。
- 前置條件：G2 PASS。
- 操作要求：區分使用者原話、已確認事實、推論、假設、UNKNOWN 與待問問題。
- 禁止事項：不得把推論寫成需求；不得先決定要安裝的 Skill；不得刪除原始概念。
- 檢查點：是否保留原始語意；是否問了真正阻塞執行的問題；是否產生可驗收成果。
- Acceptance Criteria：Concept Record 完整；每項目標有客觀 AC；未決與權限需求可追溯。
- Failure Handling：概念歧義但不阻塞時標假設；關鍵資料不足時 BLOCKED 並列最小問題集。
- Recovery：保留舊 Concept Record，追加 clarification revision。
- Regression Test：同一概念改變輸入格式、加入限制、移除關鍵資訊，結果應可解釋且不靜默遺失。
- 閉環條件：概念可轉成下一階段可用的能力需求，G3 PASS。
- 負責角色：IMPLEMENTER／TESTER／INDEPENDENT_AUDITOR。
- 證據與保存：`schemas/concept-record.schema.md` 與原始輸入快照。
