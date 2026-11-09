<!-- 正本 PR 模板（1.2.62，ADR-085，P-19b）。每一欄都要填；沒有內容寫 NONE，不知道寫 UNKNOWN，不刪欄位。不要貼金鑰、私密字或個資，需要時寫 <KEY>、<PII>。 -->

## 改了什麼
<!-- 版本號、改動檔與每檔一句說明；局部修改的位置（檔名與段落）。 -->

## 依據
<!-- ADR 編號、MIKO 或總召裁示的訊息 id、推送授權的訊息 id。 -->

## 怎麼驗證
<!-- check_repo 結果（例：16/16 PASS，附實際命令）；測題逐案 PASS／FAIL／NOT_RUN／BLOCKED，沒實跑寫 NOT_RUN。 -->

## 稽核版 commit
<!-- miko-core §6「回報必列兩樣」之一：獨立稽核合格那版的 commit（完整 SHA）。 -->

## 兩版比對
<!-- miko-core §6「回報必列兩樣」之二：git diff 底本..稽核版 與 git diff 底本..本 PR 是否逐位元相同；不同就列出差在哪、是否只改版本號字樣。 -->

## 影響哪些 Skill
<!-- 列出受影響的 Skill 與版本；沒有寫 NONE。 -->

## 還沒確認的
<!-- UNKNOWN、NOT_READ、NOT_RUN 逐條列出；沒有寫 NONE。 -->

## 回滾方式
<!-- 例：git revert -m 1 <合併 commit>，依 miko-core §7 取得推送授權後再 git push origin main；Drive DELTA 怎麼標作廢。 -->
