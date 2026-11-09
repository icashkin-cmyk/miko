# test_terms_check.py｜terms_check.py 的固定題（1.2.53，ADR-076）：python3 -I -B skills/miko-core/scripts/test_terms_check.py
import subprocess, sys, tempfile, pathlib
HERE = pathlib.Path(__file__).resolve().parent
OK_BLOCK = '''### 甲詞（正式名稱：甲類的完整說法）【檢核】
- 定義：〈定義〉
- 觸發條件：〈觸發〉
- 執行動作：〈動作〉
- 輸出／證據：〈輸出〉
- 完成判準：〈完成〉
- 失敗處理：〈失敗〉
- 條文：§1
'''
CORE = '---\nname: x\ndescription: 甲詞\n---\n\n# 標題 v1 甲詞\n> 名詞：甲詞（正式名稱：甲類的完整說法）【檢核】\n\n## 名詞表\n' + OK_BLOCK + '\n## 1. 其他\n甲詞照做。\n'
def run(core, *files):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d)
        (p / 'core.md').write_text(core, encoding='utf-8')
        args = [sys.executable, '-I', '-B', str(HERE / 'terms_check.py'), str(p / 'core.md')]
        for i, t in enumerate(files):
            (p / f'f{i}.md').write_text(t, encoding='utf-8'); args.append(str(p / f'f{i}.md'))
        return subprocess.run(args, capture_output=True, text=True).returncode
cases = [
    ('合格樣本（名詞表齊全，名詞行在 H1 下）', run(CORE, CORE), 0),
    ('缺欄（拿掉「失敗處理」）', run(CORE.replace('- 失敗處理：〈失敗〉\n', '')), 1),
    ('欄位空白（「條文：」後沒字）', run(CORE.replace('- 條文：§1', '- 條文：')), 1),
    ('類型標籤不在五選一', run(CORE.replace('甲類的完整說法）【檢核】\n- 定義', '甲類的完整說法）【其他】\n- 定義')), 1),
    ('短名重複', run(CORE.replace('\n## 1. 其他', '\n' + OK_BLOCK + '\n## 1. 其他')), 1),
    ('沒有名詞表節', run('# 標題 v1\n內容\n'), 1),
    ('受檢檔第一次出現沒有正式名稱', run(CORE, '# 標題 v1\n這裡用甲詞。\n下一行甲詞（正式名稱：甲類的完整說法）。\n'), 1),
    ('受檢檔沒用到短名（不檢查）', run(CORE, '# 標題 v1\n無關內容\n'), 0),
    ('H1 與 frontmatter 裡的短名不算第一次出現', run(CORE, '---\nname: y\ndescription: 甲詞\n---\n# 甲詞 v1\n甲詞（正式名稱：甲類的完整說法）。\n'), 0),
    ('沒給參數', subprocess.run([sys.executable, '-I', '-B', str(HERE / 'terms_check.py')], capture_output=True).returncode, 2),
]
bad = [(n, rc, exp) for n, rc, exp in cases if rc != exp]
for n, rc, exp in cases:
    print(('PASS' if rc == exp else 'FAIL'), n, f'結束碼 {rc}（預期 {exp}）')
print(f'合計：{len(cases) - len(bad)}/{len(cases)} PASS')
sys.exit(1 if bad else 0)
