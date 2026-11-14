---
doc_id: uac-spec
name_en: Document Contract (DOC)
name_zh: 通用產物契約
module: universal-artifact-contract
version: 0.8.7
date: 2026-11-14
status: PROPOSED
applies_to: [spec, architecture, process-design, governance-rule, router-doc, test-spec, integration-upgrade]
supersedes: 0.1.0
amends: 0.8.7
---

# 文件契約（Document Contract, DOC，原 UAC）：規格書與治理文件十六章

## 使用方式

本契約只規定「必須有哪些章節與欄位」，不規定製作順序（由 UCP 規定）。正文一律使用已驗收合格的繁體中文敘述，測試輸出、原始日誌、模型評語與待辦碎片不得寫入正文，只能放在證據目錄並以文件識別與驗收條件編號引用，此為文本純度規則（對應修正帳本規格第 2 章）。每個產物依 UCP A04 先定流程，再由流程決定哪些章節為必填；必填欄位不得刪減，選填欄位須標 `optional`。

## 1. 目的與範圍

必要欄位：`doc_id`、`name_en`、`name_zh`、`module`、`version`、`date`、`status`、`owner_role`、`supersedes`、`related_docs`、目的、範圍（含）、非範圍（不含）、適用對象。

`related_docs` 格式規則：`doc_id` 陣列；每個 `doc_id` 必須存在於本倉庫，或標為 `EXTERNAL:<uri>`；不得只寫檔名（修正 F-05）。

## 2. 名詞與定義

每個名詞一列，欄位：`term_id`、`term_zh`、`term_en`、`definition`、`source_id`、`forbidden_synonyms`（無則寫 `NONE`）。

必要欄位：`term_id`、`term_zh`、`term_en`、`definition`、`source_id`、`forbidden_synonyms`。

## 3. 問題與背景

必要欄位：現況、問題陳述、`evidence_text`（證據內容）、`evidence_source_id`（證據來源 `source_id`）、影響範圍、不處理的後果、既有嘗試。

證據必須可追溯：`evidence_source_id` 須對應 A01 來源登錄表的 `source_id`，不得寫「依經驗」或空值（修正 F-01）。

## 4. 目標狀態

必要欄位：目標、可量測指標、與現況差距、成功判準、非目標。

## 5. 流程或架構

類型分流：產物類型為架構書者，第 5、6、7 章由 ARC-1～ARC-5 取代適用；其餘產物類型維持本章。
責任邊界：本章是系統流程、系統架構與分支去向的唯一權威；UCP 只做執行與對應，不在此另行定義。

必要欄位：流程步驟或元件圖、順序與分支、邊界（起點與終點）、與 UCP 步驟 ID 的對應、異常分支去向、流程圖（`mermaid` 或 `text`）。

流程圖省略條件：僅當流程步驟 ≤3 且無分支時可寫 `NONE`；其餘一律必須提供，並於檢查器 TSV-CONTRACT 判定（修正 F-02）。

## 6. 元件與責任

適用範圍：一般文件；架構書改用 ARC-1 系統元件與責任配置。
責任邊界：本章是元件、責任、介面與連接關係的唯一權威；UCP 只驗證執行是否符合，不重寫元件表。

每個元件一列，欄位：`component_id`、responsibility、not_responsible、owner_role、inputs、outputs、single_owner（`true`／`false`）。

必要欄位：`component_id`、responsibility、not_responsible、owner_role、inputs、outputs、single_owner。

## 7. 輸入與輸出

適用範圍：一般文件；架構書改用 ARC-2 介面與連接、ARC-3 資料流與依賴。
責任邊界：本章是資料流、欄位、格式與傳遞方向的唯一權威；UCP 的交接步只檢查完整性並留證據。

每個 IO 一列，欄位：`io_id`、name、type、source、required、format、validation、example。

必要欄位：`io_id`、name、type、source、required、format、validation、example。

## 8. 依賴與限制

必要欄位：依賴項、依賴型別（`build-time`／`run-time`）、版本範圍、已知限制、假設、外部服務狀態（`VERIFIED`／`UNKNOWN`／`NOT_RUN`）。

## 9. 權限與邊界

必要欄位：可寫範圍、禁止範圍、授權要求、資料分級、硬禁止清單、跨平台寫入規則。

## 10. 失敗處理

必要欄位：失敗類別、偵測方式、狀態碼（限 A3 字典）、出口、重試上限（有限整數）、重試範圍、負責方。

## 11. 恢復與回復

必要欄位：回滾點、補償動作、冪等性、重入方式、資源清理、回復後重新驗證方式、回復證據位置。

## 12. 驗收條件

每條 AC 一列，欄位：`ac_id`、condition、method、evidence、judge_role、mandatory、test_case_id。

必要欄位：`ac_id`、condition、method、evidence、judge_role、mandatory、test_case_id。

## 13. 測試案例

每個案例一列，欄位：`case_id`、related_ac_id、input、expected、forbidden、actual_output（執行後填，未執行寫 `NOT_RUN`）、result。

必要欄位：`case_id`、related_ac_id、input、expected、forbidden、actual_output、result。

## 14. 回歸測試

必要欄位：回歸集清單、觸發條件（哪些修改必跑）、必跑項、通過門檻、回歸基準版本（`baseline`）、結果保存位置。

## 15. 版本與維護

必要欄位：版本（SemVer）、日期、commit（未提交時 `NOT_COMMITTED`）、SHA-256、變更紀錄、維護者、快照位置、退役規則、退役條件。

## 16. 未決事項

每項一列，欄位：`open_id`、描述、影響、負責方、解除條件、狀態（`PENDING_DECISION`／`UNKNOWN`／`BLOCKED`）。

必要欄位：`open_id`、描述、影響、負責方、解除條件、狀態。

## 附錄 A：章節與 UCP 步驟對應
對應方向為單向：每個章節指出由哪個製作步驟產生，一個章節可對多個步驟；不要求每個步驟都有章節承接，也不得反向要求 UCP 定義章節或元件。此單向規則用來斷開 UCP A04、本章第 5 章與本附錄之間的循環。

| 章節 | 對應 UCP 步驟 |
|---|---|
| 1 目的與範圍 | A03、A04 |
| 2 名詞與定義 | A05 |
| 5 流程或架構 | A04 |
| 7 輸入與輸出 | A06 |
| 10 失敗處理、11 恢復與回復 | A07 |
| 12 驗收條件、13 測試案例、14 回歸測試 | A06、A11 |
| 15 版本與維護、16 未決事項 | A13 |

## 附錄 C：名稱對照
本文件原稱 Universal Artifact Contract（UAC），自 0.8.7 起改稱文件契約（DOC），識別碼與檔名維持 uac-spec 以免斷鏈；條文編號不變。架構書類產物改用 ARC 契約。

## 附錄 B：欄位名稱權威

凡欄位名稱與 UCP 描述衝突，一律以本章為準（對應 UCP BR-05、F-10 修正）。
