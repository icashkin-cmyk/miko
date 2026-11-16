未驗收提案

# Stage 6｜Intent-to-Execution 概念到執行編排

- 目的：將已驗證的能力組合成有順序、有資料契約、有權限閘門的工作流。
- 輸入：Concept Record、Gap Matrix、Capability Inventory、已通過的候選資產、權限狀態。
- 輸出：Workflow Plan、子任務、路由選擇、資料交接、權限需求、失敗出口與驗收計畫。
- 前置條件：G5 PASS；所有必要能力至少為 callable 或明確標 BLOCKED。
- 操作要求：分開 PLANNED、CANDIDATE、AUTHORIZED、EXECUTED、VERIFIED、DELIVERED。
- 禁止事項：不得提高權限；不得把 Router 當治理；不得把規劃當執行；不得無限重試。
- 檢查點：每個子任務是否有輸入、輸出、依賴、責任、回復與終止條件。
- Acceptance Criteria：工作流可拓撲排序；無循環依賴；每個外部寫入都有授權點與回復方式。
- Failure Handling：依賴缺失 BLOCKED；執行失敗回到唯一修正目標；停滯按有限迭代規則停止。
- Recovery：回到最後可逆 checkpoint；不得覆蓋已封存成果。
- Regression Test：移除節點、打亂順序、製造循環、撤銷授權，均應被拒絕或停在 BLOCKED。
- 閉環條件：計畫、權限、資料契約與退出條件完整，G6 PASS。
- 負責角色：IMPLEMENTER／TESTER；GOVERNANCE_OWNER 授權；INDEPENDENT_AUDITOR 驗證。
- 證據與保存：Workflow Plan、DAG、router trace、permission record。
