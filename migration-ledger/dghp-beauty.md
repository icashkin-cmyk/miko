# Migration Record｜dghp-beauty

- semantic_rewrite: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- source_atom_mapping: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- governance_attachment_mixed_into_dghp_beauty: `REVOKED`
- format_validation: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- mutation_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- independent_acceptance: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- positive_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- negative_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- boundary_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- exception_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- regression_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- remote_readback: `NOT_RUN`
- runtime_status: `UNKNOWN`
- candidate_status: `REWORK_REQUIRED; NOT_ADOPTED`

撤銷原因：三角色與雙模式驗收是跨領域治理責任，不屬於美妝／醫美領域內容；已移至 `three-party-review` 與 `ai-engineering-anti-fraud-test-credibility`。

## 格式稽核撤回紀錄

- 原因：未符合 MIKO 四節、七欄指令契約與 P/C/J 執行類型，原先驗收不得作為格式合格證據。
- 下一步：依序重寫、重新 mapping、正負向／邊界／異常／回歸／Mutation 測試，再做獨立冷讀。
