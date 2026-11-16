# test_skill_lint.py｜skill_lint.py 的固定測題（make-skill AC-5）
# 用法：python3 -I -B test_skill_lint.py   全部通過結束碼 0
# 每題固定輸入（下方字串）＋預期結束碼與預期 FAIL 項；同一輸入跑兩次輸出要逐字相同（一致性）；測試只寫暫存資料夾，不改輸入（重複執行）。
import os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); LINT = os.path.join(HERE, 'skill_lint.py')
HEAD = '| ID | 類型 | 觸發條件 | 操作要求 | 禁止事項 | 驗收證據 | 失敗處理 |\n|---|---|---|---|---|---|---|\n'
def doc(rows, chk='- 題 A：expected：〈結果〉。forbidden：〈錯誤〉。\n- 題 B（相近反例，不該觸發）：expected：不載入。forbidden：開始執行。\n', solve='## 2. 解決'):
    return ('---\nname: demo\ndescription: 示範用。\n---\n\n# demo v0.1｜示範｜2026-11-08\n\n## 1. 問問題\n- 必問：〈題〉\n\n'
            f'{solve}\n{HEAD}{rows}\n## 3. 後設\n- 〈常見錯〉\n\n## 4. 檢查\n{chk}')
GOOD = '| S1 計算 | P | 收到檔案 | 跑 `python3 -I -B calc.py in.csv --out out.csv` | 手算代替（理由：會算錯） | out.csv 與預期檔 diff 為 0 | 結束碼非 0：NOT_RUN，只停 S2 |\n| S2 說明 | J | S1 通過 | 依 out.csv 寫說明 | 無 | 說明引用 out.csv 數字 | 數字不符：回 S1 |\n'
CASES = {
    'good': (doc(GOOD), 0, []),
    'empty_shell': (doc('| X1 | P | 無 | `無` | 無 | 無 | 無 |\n', chk='expected forbidden 反例\n'), 1, ['L5', 'L7', 'L8']),
    'wrong_section': (doc(GOOD, solve='## 2. 執行紀錄'), 1, ['L3', 'L4', 'L5', 'L6', 'L7', 'L9']),
    'dup_id': (doc(GOOD + GOOD.splitlines()[0] + '\n'), 1, ['L9']),
    'template_after': (doc(GOOD + '\n範本：\n| 項目 | 內容 | 出處 |\n|---|---|---|\n| 〈項〉 | 〈內容〉 | 〈第幾則〉 |\n'), 0, []),
    'blank_mid': (doc(GOOD + '\n' + '| S1 重複 | X | 收到 | 跑 `<命令>` | 無 | 輸出 | NOT_RUN |\n'), 1, ['L6', 'L9']),
    'second_table': (doc(GOOD + '\n### 子流程\n' + HEAD + '| S1 重複 | X | 收到 | 跑 `<命令>` | 無 | 輸出 | NOT_RUN |\n'), 1, ['L6', 'L9']),
    'zero_rows_template': (doc('\n範本：\n| 項目 | 內容 | 出處 |\n|---|---|---|\n| 〈項〉 | 〈內容〉 | 〈第幾則〉 |\n'), 1, ['L4']),
    'dash_mid': (doc(GOOD + '| - | - | - | - | - | - | - |\n' + '| S1 重複 | X | 收到 | 跑 `<命令>` | 無 | 輸出 | NOT_RUN |\n'), 1, ['L5', 'L6', 'L9']),
    'rows_after_template': (doc(GOOD + '\n範本：\n| 項目 | 內容 | 出處 |\n|---|---|---|\n| 〈項〉 | 〈內容〉 | 〈第幾則〉 |\n' + '\n### 續表\n' + '| S1 重複 | X | 收到 | 跑 `<命令>` | 無 | 輸出 | NOT_RUN |\n'), 1, ['L6', 'L9']),
    'template_no_sep': (doc(GOOD + '\n範本：\n| 項目 | 內容 | 出處 |\n| 〈項〉 | 〈內容〉 | 〈第幾則〉 |\n'), 0, []),
    'codeblock_example': (doc(GOOD + '\n範例：\n```\n' + HEAD + '| 〈ID〉 | 〈型〉 | 〈觸發〉 | 〈操作〉 | 〈禁止〉 | 〈證據〉 | 〈失敗〉 |\n```\n'), 0, []),
    'placeholder_cmd': (doc('| S1 計算 | P | 收到檔案 | 跑 `<命令>` | 無 | 輸出檔 | NOT_RUN |\n'), 1, ['L7']),
}
def run(*args): return subprocess.run([sys.executable, '-I', '-B', LINT, *args], capture_output=True, text=True)
class T(unittest.TestCase):
    def test_cases(self):
        with tempfile.TemporaryDirectory() as d:
            for name, (text, rc, fails) in CASES.items():
                p = os.path.join(d, f'{name}.md')
                with open(p, 'w', encoding='utf-8') as f: f.write(text)
                a, b = run(p), run(p)
                self.assertEqual(a.returncode, rc, f'{name} 結束碼\n{a.stdout}')
                self.assertEqual(a.stdout, b.stdout, f'{name} 兩次輸出不同')
                got = sorted({ln.split()[1] for ln in a.stdout.splitlines() if ln.strip().startswith('FAIL L')})
                self.assertEqual(got, sorted(fails), f'{name} FAIL 項\n{a.stdout}')
                with open(p, encoding='utf-8') as f: self.assertEqual(f.read(), text, f'{name} 輸入被改動')
    def test_no_args(self): self.assertEqual(run().returncode, 2)
if __name__ == '__main__': unittest.main()
