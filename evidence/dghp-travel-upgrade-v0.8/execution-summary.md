# dghp-travel v0.8 累積式升級驗收摘要

- Candidate: v0.8-cumulative-candidate
- Previous snapshot: v0.7-rewritten-candidate
- Old SHA-256: 76f16de181900a2c3201446b199554af857cf2d72af471cb48bd0f039012fd0e
- New SHA-256: 15090182e20acef3f755e206425740f63e92ae8708098c45ee9854caa679e49f
- Source SHA-256: 22d0ecc87092eee1e3b496d0811bc3f813e236cdf9e0eec5a577c425879d01eb

## 實際結果

- quick_validate: PASS；stdout/stderr 已保存。
- skill_lint: PASS 9/9；stdout/stderr 已保存。
- `source_atom_mapping`：第一次 FAIL（候選 Hash 未同步，後續發現 fixture 欄位名不符驗證器契約）；已記錄於 `previous-failure.md` 與 `mapping-repair-record.md`；修正後重跑 PASS，50/50；`source_atom_mapping_rerun.stdout` 與 stderr 已保存。
- regression_unittest: PASS；stdout/stderr 已保存。
- preservation-check: PASS；stdout/stderr 已保存。
- `route-mutation`：前一輪 FAIL，已記錄於 `previous-failure.md`；修正 harness 後 PASS，實際輸出已保存於 `route-mutation.stdout`、`route-mutation.stderr` 與 `route-mutation.exit-code`。

## 狀態邊界

詳見 `status-matrix.md`。目前使用版本為 `UNKNOWN`、正式採用為 `PENDING`、GitHub 遠端讀回為 `NOT_RUN`、Runtime 生效為 `UNKNOWN`；本輪獨立驗收 A–G 為 `PASS`，但不得宣稱正式採用或 Runtime 生效。
