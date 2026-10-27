# 各平台啟動設定（一次貼上，之後自動讀最新正本）

正本：https://raw.githubusercontent.com/icashkin-cmyk/miko/main/README.md
版本：https://raw.githubusercontent.com/icashkin-cmyk/miko/main/VERSION
測試句（每個平台開新對話貼上）：「你好，回報 MIKO 版本、目前總召是誰、說『收工』時你會做什麼」
通過條件：第一行出現正本版本（目前是 VERSION 的 1.2.1；Claude 寫成「正本 v1.2.1」）；總召回答 Claude；收工答出交接欄位、存檔與任務四態。只印版本、答不出收工內容不算通過。Claude 區塊必須和治理房最新的偏好檔逐字相同。完整回歸測試見正本 §8。

網址不保證每個平台每次都讀得到。ChatGPT 專案、Gemini Gem 另外上傳一份 README.md 當副本（專案檔或知識檔），正本改版時一起換；讀到副本時對齊行標「副本 vX」。各平台改編版（例如 miko-core-gpt）要寫明根據的正本版本，低於正本就以正本為準。

## Claude（設定 → 個人偏好，取代原【開工對齊】一行）
```
【開工對齊】每個新對話的第一個任務前，先載入 miko-core Skill（常駐，內含閉環、四視角與治理）完成開工對齊並核對 MIKO 正本版本（github.com/icashkin-cmyk/miko），再依功能指令表調用通用或任務 Skill；第一則回覆第一行回報對齊結果與版本。載入不到時標 CORE_NOT_READ：找檔、澄清、安全回應與其他不依賴核心的低風險工作照做，不做外部寫入與不可逆操作。
```

## ChatGPT（自訂指令已 4,995／5,000 字放不下，改用記憶：在 ChatGPT 對話中貼下面這句，確認它回「已更新記憶」）
```
請記住：每個新對話的第一個任務前，先讀 https://raw.githubusercontent.com/icashkin-cmyk/miko/main/README.md 的 MIKO 正本並照做；正本優先於我的自訂指令中的同類規則；讀不到網址就讀本專案裡的 README.md 副本；都讀不到就在第一行標「MIKO 正本 NOT_READ」，照自訂指令繼續，但不做外部寫入與不可逆操作。
```
自訂指令有空位時，可改放同一句到自訂指令最前面。

## Codex（同步指示或全域 AGENTS.md，放在最前面）
```
開始任務前先取得 MIKO 正本：有網路時先執行 git -C ~/miko pull --ff-only（或直接讀 https://raw.githubusercontent.com/icashkin-cmyk/miko/main/README.md），再讀 ~/miko/README.md；沒有網路時讀 ~/miko/README.md 上次同步的版本，並在第一行標「正本離線版（VERSION 值）」。正本優先於本設定中的同類規則；都讀不到時標「MIKO 正本 NOT_READ」並用本設定繼續，但不做外部寫入與不可逆操作。
```
本機一次性準備（終端機）：
```
git clone https://github.com/icashkin-cmyk/miko.git ~/miko
```

## Gemini（Gem 的指示，或「已儲存的資訊」）
```
每次對話第一個任務前，先開啟 https://raw.githubusercontent.com/icashkin-cmyk/miko/main/README.md 讀 MIKO 正本並照做；第一行回報 MIKO 版本；讀不到網址就讀 Gem 知識檔裡的 README.md 副本；都讀不到就說「MIKO 正本 NOT_READ」，不做外部寫入與不可逆操作。
```
Gemini 的 GitHub「Import code」只能讀、每個對話匯入一次、內容是匯入當下的快照，正本改版不會同步，所以不能取代上面這句設定，只適合單次測試。
