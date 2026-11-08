# test_photo_scripts.py｜照片 Skill 程式的冒煙測試（正本 1.2.42，ADR-065；CI 每次推送與 PR 都跑）
# 用法：python3 -I -B tests/test_photo_scripts.py   全部通過結束碼 0
# 只讀 skills/photo-inspection-log/scripts 的整包、不寫入 repo；暫存檔只寫系統暫存資料夾。
# 照片 Skill 的 writer 是照片專案：本檔只測現行行為，不改照片程式。
# preflight「有 FAIL 時結束碼要非 0」的測試在照片專案修好前不放進來（現況結束碼為 0，提案見專案檔 handoff/Boris工作法_20261108/）。
import os, shutil, subprocess, sys, tempfile, unittest
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SD = os.path.join(R, 'skills', 'photo-inspection-log', 'scripts')
PF = os.path.join(SD, 'preflight.py')
def run(*args, cwd=None): return subprocess.run([sys.executable, '-I', '-B', *args], capture_output=True, text=True, cwd=cwd)
class T(unittest.TestCase):
    def test_start_full_package(self):
        # 整包齊全：每項 PASS、沒有 FAIL、結論「全部 PASS」、結束碼 0
        r = run(PF, 'start')
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertGreaterEqual(sum(1 for x in lines if x.startswith('PASS ')), 13, r.stdout)
        self.assertFalse([x for x in lines if x.startswith('FAIL ')], r.stdout)
        self.assertIn('全部 PASS，可以開始', r.stdout)
    def test_start_missing_package_reports_fail(self):
        # 只有 preflight.py 時要逐項印 FAIL 並寫「有 FAIL，停止」（只驗輸出內容；結束碼待照片專案修正）
        with tempfile.TemporaryDirectory() as d:
            shutil.copy(PF, d)
            r = run(os.path.join(d, 'preflight.py'), 'start', cwd=d)
            self.assertEqual(sum(1 for x in r.stdout.splitlines() if x.startswith('FAIL ')), 5, r.stdout)
            self.assertIn('有 FAIL，停止', r.stdout)
    def test_scripts_compile(self):
        # 四支程式語法正確（只編譯不執行）
        for f in ['log_photo.py', 'make_entries.py', 'build_company.py', 'preflight.py']:
            with open(os.path.join(SD, f), encoding='utf-8') as fh:
                compile(fh.read(), f, 'exec')
if __name__ == '__main__':
    unittest.main(verbosity=1)
