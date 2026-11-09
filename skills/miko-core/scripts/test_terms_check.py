# test_terms_check.py｜terms_check.py 的固定題（1.2.53，ADR-076）：python3 -I -B skills/miko-core/scripts/test_terms_check.py
import subprocess, sys, tempfile, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SECS = ['正式名稱', '類型', '定義', '觸發條件', '執行動作', '輸出格式', '完成判準', '失敗處理', '不適用情況', '相關名詞', '條文']
def term(name, formal, tag='【檢核】', skip=None, val=None):
    out = [f'## {name}']
    for k in SECS:
        if k == skip: continue
        out += [f'### {k}', formal if k == '正式名稱' else tag if k == '類型' else (val if val is not None else f'〈{k}內容〉')]
    return '\n'.join(out) + '\n'
DEFS = '# 定義表 v1\n\n' + term('甲詞', '甲類的完整說法') + '\n' + term('乙詞', '含甲詞字樣的乙類說法', '【處置】')
GOOD = '---\nname: x\ndescription: 甲詞\n---\n\n# 標題 v1 甲詞\n\n> 名詞：甲詞（正式名稱：甲類的完整說法）【檢核】。\n\n正文用甲詞。\n'
def run(defs, *files):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d); (p / 'defs.md').write_text(defs, encoding='utf-8')
        args = [sys.executable, '-I', '-B', str(HERE / 'terms_check.py'), str(p / 'defs.md')]
        for i, t in enumerate(files):
            (p / f'f{i}.md').write_text(t, encoding='utf-8'); args.append(str(p / f'f{i}.md'))
        return subprocess.run(args, capture_output=True, text=True).returncode
cases = [
    ('合格樣本', run(DEFS, GOOD), 0),
    ('缺一節（不適用情況）', run('# 表\n' + term('甲詞', '甲類的完整說法', skip='不適用情況')), 1),
    ('節內容空白', run('# 表\n' + term('甲詞', '甲類的完整說法', val='')), 1),
    ('節內容只指回（見 §1）', run('# 表\n' + term('甲詞', '甲類的完整說法', val='見 §1')), 1),
    ('類型不在五選一', run('# 表\n' + term('甲詞', '甲類的完整說法', tag='【其他】')), 1),
    ('短名重複', run(DEFS + '\n' + term('甲詞', '另一個說法')), 1),
    ('正式名稱重複', run(DEFS + '\n' + term('丙詞', '甲類的完整說法')), 1),
    ('沒有任何名詞', run('# 表\n內容\n'), 1),
    ('第一次出現沒有正式名稱', run(DEFS, '# 標題 v1\n\n> 名詞：無\n\n這裡用甲詞。\n甲詞（正式名稱：甲類的完整說法）。\n'), 1),
    ('同行有正式名稱字串但不緊鄰短名', run(DEFS, '# 標題 v1\n\n> 名詞：甲詞是甲類的完整說法\n'), 1),
    ('正式名稱裡含另一短名不誤擋（乙詞的正式名稱含「甲詞」）', run(DEFS, '# 標題 v1\n\n> 名詞：乙詞（正式名稱：含甲詞字樣的乙類說法）【處置】。\n'), 0),
    ('名詞行不在 H1 下第一個非空行', run(DEFS, '# 標題 v1\n\n內容\n\n> 名詞：甲詞（正式名稱：甲類的完整說法）【檢核】。\n'), 1),
    ('程式碼區塊裡的「# 」不當成 H1、區塊內短名不算', run(DEFS, '```\n# 註解 甲詞\n```\n# 標題 v1\n\n> 名詞：甲詞（正式名稱：甲類的完整說法）【檢核】。\n'), 0),
    ('受檢檔沒用到短名（不檢查）', run(DEFS, '# 標題 v1\n無關內容\n'), 0),
    ('frontmatter 與 H1 裡的短名不算第一次出現', run(DEFS, GOOD), 0),
    ('名詞行類型標籤錯（【其他】）', run(DEFS, '# 標題 v1\n\n> 名詞：甲詞（正式名稱：甲類的完整說法）【其他】。\n'), 1),
    ('正式名稱後多字（前綴不算）', run(DEFS, '# 標題 v1\n\n> 名詞：甲詞（正式名稱：甲類的完整說法加字）【檢核】。\n'), 1),
    ('正文第一次出現用「；」接出處（允許）', run(DEFS, '# 標題 v1\n\n> 名詞：另述\n\n- 甲詞（正式名稱：甲類的完整說法；1.2.53）：內容\n'), 0),
    ('名詞行拆兩行，第二行的類型標籤錯也要擋', run(DEFS, '# 標題 v1\n\n> 名詞：乙詞（正式名稱：含甲詞字樣的乙類說法）【處置】；\n> 甲詞（正式名稱：甲類的完整說法）【其他】。\n'), 1),
    ('定義表「類型」節前多空行仍檢查標籤', run(DEFS.replace('### 類型\n【檢核】', '### 類型\n\n【檢核】'), '# 標題 v1\n\n> 名詞：甲詞（正式名稱：甲類的完整說法）。\n'), 1),
    ('沒給參數', subprocess.run([sys.executable, '-I', '-B', str(HERE / 'terms_check.py')], capture_output=True).returncode, 2),
]
bad = [c for c in cases if c[1] != c[2]]
for n, rc, exp in cases:
    print(('PASS' if rc == exp else 'FAIL'), n, f'結束碼 {rc}（預期 {exp}）')
print(f'合計：{len(cases) - len(bad)}/{len(cases)} PASS')
sys.exit(1 if bad else 0)
