# 前一輪失敗維護紀錄

## 1. route-mutation 初次失敗

- 測試：route-mutation
- 結果：FAIL
- 現象：原 mutation harness 只替換第一個 `version-evolution-preservation` 字串；正文其他位置仍保留該字串，因此 mutation 沒有被拒絕，程式以 `AssertionError` 結束。
- 影響：不得把 v0.8 標記為 `QUALIFIED_FOR_NEXT_STAGE`。
- 修正：改為替換所有版本保護路由引用，再確認 validator 拒絕 mutated text。
- 重測證據：`route-mutation.stdout`、`route-mutation.stderr`、`route-mutation.exit-code`。

## 2. source_atom_mapping 初次失敗

- 測試：source_atom_mapping
- 結果：FAIL
- 實際證據：`source_atom_mapping.stderr` 記錄 candidate SHA assertion 失敗；更新候選版本後 Hash 尚未同步。
- 後續發現：mapping fixture 使用 `status`，但 `validate_mapping.py` 要求 `mapping_status`，造成 KeyError。
- 修正：同步 candidate SHA；將 fixture 欄位由 legacy `status` 更名為 validator 要求的 `mapping_status`，mapping 語意與 50 個原子未改變。
- 重測證據：`source_atom_mapping_rerun.stdout` 顯示 `candidate_anchor_coverage=50/50`、`orphan_source_atoms=0`、`mapping_result=PASS`。

前述失敗證據全部保留，不以最終 PASS 覆蓋歷史失敗。
