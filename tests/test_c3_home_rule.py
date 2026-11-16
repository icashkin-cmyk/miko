"""C3 的本機家目錄路徑規則測試：通用沙盒家目錄（ubuntu、user、runner）不擋，其他家目錄路徑照擋；
email、macOS 使用者路徑、波浪號大寫開頭 維持照擋。從 tests/check_repo.py 取出 C3 的 pat 那一行實跑。"""
import pathlib, re, sys

H = '/ho' + 'me/'   # 測資用拼接，避免這個測試檔自己被 C3 掃到
U = '/Us' + 'ers/'
AT = '@' + 'example.com'

src = (pathlib.Path(__file__).resolve().parent / 'check_repo.py').read_text(encoding='utf-8')
line = next(l for l in src.splitlines() if l.startswith('pat = re.compile('))
ns = {'re': re, 'words': []}
exec(line, ns)
pat = ns['pat']

SHOULD_PASS = [H + 'ubuntu/upload/a.txt', H + 'ubuntu', '`' + H + 'ubuntu/work/x`', '"' + H + 'user/app"', H + 'runner/work/miko/miko', H + 'ubuntu\n']
SHOULD_HIT = [H + 'alice/x', H + 'ubuntu2/x', H + 'ubuntu_alice/x', H + 'ubuntu-x/x', H + 'userx/x', H, H + 'Ubuntu/x',
              U + 'alice/x', '~' + '/Documents', 'someone' + AT, 'a.b+c@x-y' + '.tw']
bad = [s for s in SHOULD_PASS if pat.search(s)] + [s for s in SHOULD_HIT if not pat.search(s)]
print('FAIL' if bad else 'PASS', f'不該命中卻命中或該命中卻漏掉：{bad}', f'共 {len(SHOULD_PASS) + len(SHOULD_HIT)} 題')
sys.exit(1 if bad else 0)
