# Mapping 驗證器修復紀錄

## 原始問題

導入前候選 mapping fixture 使用過時欄位與固定數量：部分 atom 使用 `status` 而非 `mapping_status`，部分缺少 `source_atom_id`；治理 Skill 使用聚合 `S1-S4` anchor；dghp-beauty 與 dghp-food 的固定 atom 數分別仍寫 53 與 40，但實際 fixture 為 61 與 54。

## 修復方式

- `status` → `mapping_status`：保留原值，不改變映射狀態。
- `id` → `source_atom_id`：保留原 `id`，補上驗證器要求的相容欄位。
- 治理 Skill：將過時聚合 anchor 改為實際存在的 `UC1`～`UC4` 與章節 anchor。
- dghp-beauty：將過時聚合 anchor 改為實際存在的 `references/pre-format-candidate-SKILL.md` 與 `SB-001`～`SB-053`。
- dghp-beauty／dghp-food 驗證器：固定數量更新為實際且唯一的 61／54；沒有刪除 atom。
- 所有 source／candidate SHA-256 依新分支實際內容重算。

## 結果

`tests/manus-candidate/*/validate_mapping.py` 共 6 組，實際執行結果：`6/6 PASS`。這些修復只作用於候選測試與證據，不修改 MIKO main，也不降低映射覆蓋條件。
