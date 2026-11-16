# Migration Record｜dghp-food

- source_sha256: `d1bedcf85833ad0ee32da219d1d5fa2622ce2a3dac471474a6c265473451279d`
- candidate_sha256: `e3a4ffd99d2d032f0fe18f05a506644abe30255f538f5ec78bc5a019f7a61950`
- source_atoms: `40`
- semantic_rewrite: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- source_atom_mapping: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- positive_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- negative_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- boundary_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- exception_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- regression_tests: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- independent_acceptance: `NOT_RUN`（MIKO 正式格式稽核不合格，舊 PASS 撤回）
- candidate_status: `REWORK_REQUIRED; NOT_ADOPTED`

## 格式稽核撤回紀錄

- 原因：未符合 MIKO 四節、七欄指令契約與 P/C/J 執行類型，原先驗收不得作為格式合格證據。
- 下一步：依序重寫、重新 mapping、正負向／邊界／異常／回歸／Mutation 測試，再做獨立冷讀。
