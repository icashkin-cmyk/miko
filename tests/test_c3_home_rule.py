"""C3 的 /home/ 規則測試：通用沙盒家目錄（ubuntu、user、runner）不擋，其他 /home/ 路徑照擋；
email、/Users/、~/大寫開頭 維持照擋。從 tests/check_repo.py 取出 C3 的 pat 那一行實跑。"""
import pathlib, re, sys

src = (pathlib.Path(__file__).resolve().parent / 'check_repo.py').read_text(encoding='utf-8')
line = next(l for l in src.splitlines() if l.startswith('pat = re.compile('))
ns = {'re': re, 'words': []}
exec(line, ns)
pat = ns['pat']

SHOULD_PASS = ['/home/ubuntu/upload/a.txt', '/home/ubuntu', '`/home/ubuntu/work/x`', '"/home/user/app"', '/home/runner/work/miko/miko', '/home/ubuntu\n']
SHOULD_HIT = ['/home/alice/x', '/home/ubuntu2/x', '/home/ubuntu_alice/x', '/home/ubuntu-x/x', '/home/userx/x', '/home/', '/home/Ubuntu/x',
              '/Users/alice/x', '~/Documents', 'someone@example.com', 'a.b+c@x-y.tw']
bad = [s for s in SHOULD_PASS if pat.search(s)] + [s for s in SHOULD_HIT if not pat.search(s)]
print('FAIL' if bad else 'PASS', f'不該命中卻命中或該命中卻漏掉：{bad}', f'共 {len(SHOULD_PASS) + len(SHOULD_HIT)} 題')
sys.exit(1 if bad else 0)
