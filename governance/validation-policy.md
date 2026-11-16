# Skill 驗收分層政策

## 核心責任分層

`miko-core` 是常駐核心 Skill，負責閉環、四視角、治理、品質閘門、路由與硬邊界；它不是領域 Skill，因此不適用領域 Skill 的四節與 P/C/J 七欄 linter。對 `miko-core` 採核心專用驗收：frontmatter、版本／正本對應、閉環、四視角、治理、硬邊界、失敗處理、共同整合路由與原有 MIKO 回歸測試。

其餘 19 個 Skill 是通用或任務 Skill，必須通過 `quick_validate.py`、領域 `skill_lint.py`、共同累積式整合路由、低於 500 行與各自功能／邊界／回歸測試。

## 禁止事項

不得為了讓 `miko-core` 通過領域 linter 而把核心責任硬拆成領域四節；不得把核心例外解讀為免除版本保護、衝突檢查或獨立驗收。
