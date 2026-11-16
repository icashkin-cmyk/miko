# Migration Record｜dghp-metaphysical-integrated-analysis

- source_commit: `ec80f473695305b35b90f0ebb941431ddde4626e`
- source_version: `1.2.72`
- source_skill_sha256: `546f1feac8424db1bfd7b2a7a8f7e42437a360fc90149d27779be7e1b3484cc7`
- candidate_skill_sha256: `a2b62ebcc4835bd049a8c9a551045e2dd672336a6712b4c81077adaa500d2e2b`
- source_atoms: `61`
- format_validation: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- semantic_rewrite: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- source_atom_mapping: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- positive_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- negative_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- boundary_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- exception_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- regression_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- mutation_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- independent_acceptance: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- remote_readback: `NOT_RUN`
- runtime_status: `UNKNOWN`
- candidate_status: `REWORK_REQUIRED; NOT_ADOPTED`

## 格式稽核撤回紀錄

- 原因：未符合 MIKO 四節、七欄指令契約與 P/C/J 執行類型，原先驗收不得作為格式合格證據。
- 下一步：依序重寫、重新 mapping、正負向／邊界／異常／回歸／Mutation 測試，再做獨立冷讀。
