# Migration Record｜dghp-travel

- source_commit: `ec80f473695305b35b90f0ebb941431ddde4626e`
- source_version: `1.2.72`
- source_skill_sha256: `22d0ecc87092eee1e3b496d0811bc3f813e236cdf9e0eec5a577c425879d01eb`
- candidate_skill_sha256: `76f16de181900a2c3201446b199554af857cf2d72af471cb48bd0f039012fd0e`
- source_atoms: `50`
- format_validation: `PASS`
- semantic_rewrite: `PASS`
- source_atom_mapping: `PASS`
- positive_tests: `PASS`
- negative_tests: `PASS`
- boundary_tests: `PASS`
- exception_tests: `PASS`
- regression_tests: `PASS`
- mutation_tests: `PASS`
- independent_acceptance: `PASS`
- remote_readback: `NOT_RUN`
- runtime_status: `UNKNOWN`
- candidate_status: `QUALIFIED_FOR_NEXT_STAGE; CANDIDATE_NOT_ADOPTED`

## 格式修正紀錄

- 舊判定撤回原因：前版僅為 preservation-first 加註與逐字 mapping，未符合 MIKO 四節、七欄與 P/C/J 格式。
- 修正內容：改寫為四節；T1～T6 補齊七欄；P 步加入可執行命令；檢查節加入 expected、forbidden 與相近反例。
- 修正後 linter：`PASS 9/9`。

## 累積式升級 v0.8

- previous_candidate_version: `v0.7-rewritten-candidate`
- previous_candidate_sha256: `76f16de181900a2c3201446b199554af857cf2d72af471cb48bd0f039012fd0e`
- candidate_version: `v0.8-cumulative-candidate`
- candidate_skill_sha256: `15090182e20acef3f755e206425740f63e92ae8708098c45ee9854caa679e49f`
- upgrade_type: `CUMULATIVE_ROUTE_ENHANCEMENT`
- inherited: `T1-T6、AC-T1～AC-T6、既有旅遊規則與限制`
- strengthened: `description 明確路由至 version-evolution-preservation`
- added: `0.1 累積式升級與歷史版本保護路由`
- corrected: `補足升級前快照、diff、Hash、回歸與不得升格規則`
- refactored: `NONE`
- deprecated: `NONE`
- old_snapshot: `archive/dghp-travel/v0.7-rewritten-candidate/SKILL.md`
- diff: `evidence/dghp-travel-upgrade-v0.8/v0.7-to-v0.8.diff`
- failure_history: `evidence/dghp-travel-upgrade-v0.8/previous-failure.md`
- mapping_repair: `evidence/dghp-travel-upgrade-v0.8/mapping-repair-record.md`
- regression: `PASS`
- route_mutation: `PASS`
- independent_acceptance_v0.8: `PASS`
- remote_readback: `NOT_RUN`
- runtime_status: `UNKNOWN`
- formal_adoption: `PENDING`
- candidate_status: `QUALIFIED_FOR_NEXT_STAGE; CANDIDATE_NOT_ADOPTED`
