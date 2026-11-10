# test_flowlock_check.py｜flowlock_check.py 的固定測題（1.2.64，ADR-087；P-19a 先寫會失敗的重現，再寫程式；只用標準函式庫）
# 用法：python3 -I -B skills/miko-core/scripts/test_flowlock_check.py；全過結束碼 0
import subprocess, sys, tempfile, pathlib
S = pathlib.Path(__file__).resolve().parent / 'flowlock_check.py'
CASES = [
    # (名稱, 回覆全文, 預期結束碼)
    ('三數相加等於標籤數', '結論 A【來源：README 1.2.63】。\n數字 3【工具：wc -l】。\n推估 B【推論】。\n\n流程鎖：通過 2 項／降級 1 項／UNKNOWN 0 項（降級：B【推論】）', 0),
    ('通過數多報（T60A 型：宣告 7、可數 6）', '甲【來源：x】乙【來源：y】丙【工具：z】\n丁【使用者】戊【常識】己【工具：w】\n\n流程鎖：通過 7 項／降級 0 項／UNKNOWN 0 項', 1),
    ('通過數少報（T60C 型：宣告 2、可數 3）', '甲【來源：x】乙【使用者】丙【工具：z】\n\n流程鎖：通過 2 項／降級 0 項／UNKNOWN 0 項', 1),
    ('降級與 UNKNOWN 分類錯（推論算成通過）', '甲【來源：x】乙【推論】丙【UNKNOWN】\n\n流程鎖：通過 2 項／降級 0 項／UNKNOWN 1 項', 1),
    ('流程鎖括號內的標籤不重複計數', '甲【來源：x】乙【未查證】\n\n流程鎖：通過 1 項／降級 1 項／UNKNOWN 0 項（降級：乙【未查證】）', 0),
    ('程式碼區塊內的標籤不計數', '甲【來源：x】\n```\n範例【推論】【工具：y】\n```\n\n流程鎖：通過 1 項／降級 0 項／UNKNOWN 0 項', 0),
    ('規則類型標籤不計數', '本段【流程】【輸出】【檢核】【限制】【處置】甲【工具：x】\n\n流程鎖：通過 1 項／降級 0 項／UNKNOWN 0 項', 0),
    ('流程鎖不在最後一行（§5 第 5 點）', '甲【來源：x】\n\n流程鎖：通過 1 項／降級 0 項／UNKNOWN 0 項\n補充一句', 1),
    ('沒有流程鎖行', '甲【來源：x】', 1),
    ('帶補充說明的標籤照前綴分類', '甲【推論，只加句不刪】乙【未查證：上游日期】丙【UNKNOWN】\n\n流程鎖：通過 0 項／降級 2 項／UNKNOWN 1 項', 0),
    ('有交付檔字樣仍照算', '甲【來源：x】\n\n流程鎖：通過 1 項／降級 0 項／UNKNOWN 0 項（完整版見交付檔〈a.md〉）', 0),
]
fails = 0
with tempfile.TemporaryDirectory() as d:
    for i, (name, text, want) in enumerate(CASES, 1):
        f = pathlib.Path(d) / f'c{i}.md'
        f.write_text(text, encoding='utf-8')
        r = subprocess.run([sys.executable, '-I', '-B', str(S), str(f)], capture_output=True, text=True)
        good = r.returncode == want
        fails += not good
        print(('PASS' if good else 'FAIL'), f'{i:02d} {name}｜預期結束碼 {want}，實際 {r.returncode}', '' if good else (r.stdout + r.stderr)[:200])
print(f'合計：{len(CASES) - fails}/{len(CASES)} PASS')
sys.exit(1 if fails else 0)
