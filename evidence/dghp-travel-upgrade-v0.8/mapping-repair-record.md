# source_atom_mapping 維護紀錄

第一次執行 `python3 tests/dghp-travel/validate_mapping.py` 時，候選 Hash 尚未同步，實際 stderr 為 candidate SHA assertion failure。同步 Hash 後再次執行，驗證器發現既有 fixture 欄位名為 `status`，而驗證器契約要求 `mapping_status`，因此產生 KeyError。

本次修正只處理測試 fixture 與候選版本 metadata：將每個原子欄位改成 `mapping_status`，沒有刪除、合併或改寫 50 個 source atoms。重跑結果保存於 `source_atom_mapping_rerun.stdout` 與 `source_atom_mapping_rerun.stderr`，實際結果為：`source_sha256=PASS`、`candidate_sha256=PASS`、`atom_count=50`、`candidate_anchor_coverage=50/50`、`orphan_source_atoms=0`、`mapping_result=PASS`。
