未驗收提案

# MIKO Universal Governance Architecture v0.1.0-candidate.2

- 提案狀態：`CANDIDATE`／`NOT_ADOPTED`
- stable_id：`miko-universal-governance-architecture`
- proposed_version：`0.1.0-candidate.2`
- proposed_branch：`manus/miko-universal-governance-v0.1.0-candidate.2`
- base_branch：`main`
- target_repository：`icashkin-cmyk/miko`
- 寫入範圍：本提案檔案本身；未修改 `knowledge-cards/` 以外任何 tracked file
- 正式採用：`NOT_ADOPTED`
- GitHub／Runtime 生效：本提案不宣稱

## 1. 修正摘要

本版針對上一輪 Claude 總召驗收的三項問題提出 candidate.2 修正：

1. 將檢查器改為 UTF-8 安全方式。腳本設定 `LC_ALL=C.utf8`，中文成功宣稱改用 `grep -F` 固定字串比對，不再用會在預設 C locale 位元組模式下把「、」誤當成「。」的中文字元組。ASCII 狀態欄位仍使用 ASCII-only regex。
2. 統一版本為 `0.1.0-candidate.2`。A、B、C、D、E、F、G、VERSION、README、module manifest、version ledger 與版本證據的可執行版本欄位均統一；C3 舊版號命中數為零。
3. 重建純文字 proposal manifest，重新計算所有檔案 SHA-256；提案樹不放 ZIP、tar、gz 或其他二進位檔。ZIP 不進 GitHub PR，若另行附於對話，必須另附 SHA-256。

## 2. UTF-8 安全檢查器修正

候選包中的檢查器修正為以下策略；這是候選修正內容，不是已啟用的正式 Runtime：

```bash
# Candidate 2
export LC_ALL=C.utf8

local forbidden=0
local phrase
for phrase in 'GitHub 已寫入。' 'GitHub 已寫入!' 'GitHub 已寫入.' \
  'GitHub 已經推送。' 'GitHub 已經生效。' \
  'Runtime 已啟用。' 'Runtime 已生效。'; do
  if grep -R -F -n \
    --exclude='MANIFEST.sha256' \
    --exclude='*.zip' \
    --exclude='init-local-github-tree.sh' \
    -- "$phrase" "$ROOT" >/dev/null; then
    forbidden=1
  fi
done
```

重點是 `grep -F` 與選項放在 pattern／path 之前；不使用中文字元組。檢查器仍會拒絕正向 GitHub／Runtime 生效宣稱，並保留反向 G-R12 測試。

## 3. 版本統一規則

candidate.2 的唯一可執行候選版本為：

```text
0.1.0-candidate.2
```

版本審計檢查：

```text
C3_HITS=0
C2_VERSION_FIELDS=27
```

舊版號不得出現在 candidate.2 的版本欄位、版本帳本、manifest、README 或驗收證據中。正式採用版本仍不設定；`formal_adoption` 保持 `NOT_ADOPTED`。

## 4. 實際驗證命令與輸出

以下是 candidate.2 純文字提案鏡像的實際結果；不是引用原候選包內的 PASS 自述。

### 4.1 語法檢查

```text
$ bash -n github-folder-architecture/init-local-github-tree.sh
$ bash -n tests/check-repo.sh
```

兩個命令均以 exit code 0 結束。

### 4.2 C3 與二進位檢查

```text
$ tests/check-repo.sh .
C3_HITS=0
BINARY_FILES=0
C2_VERSION_FIELDS=27
```

### 4.3 預設 C locale

```text
$ LC_ALL=C bash github-folder-architecture/init-local-github-tree.sh check .
PASS: G-AC-01 required directory responsibility check
PASS: G-AC-02 naming and uniqueness check
PASS: G-AC-03 README and module manifest check
PASS: G-AC-04 canonical/snapshot/archive separation check
PASS: G-AC-05 formal GitHub/Runtime boundary check
PASS: G-AC-06 A-F read-only boundary check
CHECK_PASS root=.

$ LC_ALL=C bash github-folder-architecture/init-local-github-tree.sh reverse-test .
REVERSE_TEST_PASS cases=12
```

### 4.4 UTF-8 locale

```text
$ LC_ALL=C.UTF-8 bash github-folder-architecture/init-local-github-tree.sh check .
PASS: G-AC-01 required directory responsibility check
PASS: G-AC-02 naming and uniqueness check
PASS: G-AC-03 README and module manifest check
PASS: G-AC-04 canonical/snapshot/archive separation check
PASS: G-AC-05 formal GitHub/Runtime boundary check
PASS: G-AC-06 A-F read-only boundary check
CHECK_PASS root=.

$ LC_ALL=C.UTF-8 bash github-folder-architecture/init-local-github-tree.sh reverse-test .
REVERSE_TEST_PASS cases=12
```

### 4.5 Self-test

```text
$ bash github-folder-architecture/init-local-github-tree.sh self-test
REVERSE_TEST_PASS cases=12
SELF_TEST_PASS
```

## 5. Manifest 與 SHA-256

candidate.2 純文字 proposal mirror 的 MANIFEST 共 102 筆，已執行：

```text
$ sha256sum -c MANIFEST.sha256
102/102 PASS
```

`MANIFEST.sha256` 本身的 SHA-256：

```text
03b88d2408fdc03709a5e99df8441294be8d8d706e787dfbb6814419451f4df6
```

本 Draft PR 不放 ZIP 或其他二進位。ZIP 狀態：`NOT_CREATED`／`NOT_APPLICABLE`。若後續依對話要求另行產生 ZIP，只能作為對話附件，並必須附其獨立 SHA-256，不得提交到 `knowledge-cards/`。

## 6. 本次 PR 的檔案邊界

本分支預期只新增本檔案：

```text
knowledge-cards/proposals/docs/20261115_miko-universal-governance-v0.1.0-candidate.2.md
```

不得修改：

```text
VERSION
skills/
sync/
tests/
.github/
其他 knowledge-cards/ 以外路徑
```

本文件是提案，不是正式規則；不得因 Draft PR 建立而宣稱正式採用、Runtime 熱插拔、Claude Code、Manus 或 GitHub 正本已生效。

## 7. 驗收與放行狀態

| 項目 | 狀態 |
|---|---|
| C locale check | `PASS` |
| UTF-8 locale check | `PASS` |
| C3 舊版號命中 | `0` |
| G-AC-01～G-AC-06 | `PASS` |
| G-R01～G-R12 | `12/12 PASS` |
| manifest SHA-256 | `102/102 PASS` |
| ZIP binary in PR | `0` |
| formal adoption | `NOT_ADOPTED` |
| Runtime activation | `NOT_RUN`／`UNKNOWN` |
| Claude 總召正式放行 | `待獨立複核` |
