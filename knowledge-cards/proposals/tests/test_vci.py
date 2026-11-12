#!/usr/bin/env python3
# test_vci.py｜vci_media.py、vci_check.py 與 miko-core read_ledger.py 的固定測題（合成測資，不連網、不用真實影片、不碰回測）
# 用法：python3 -I -B test_vci.py（在本檔所在資料夾或任何位置都可）
# 沒有 ffmpeg／ffprobe 時，媒體題標 skipped（＝NOT_RUN，不算 PASS），其餘照跑；最後一行印出 PASS／NOT_RUN 計數。
# 結束碼：0＝全部 PASS 且 NOT_RUN 0；5＝沒有 FAIL 但有 NOT_RUN（不得當 PASS，稽核 r1）；1＝有 FAIL。
# 固定預期輸出放在 fixtures/（golden）：程式輸出要和檔案逐字相同，改程式行為就要同時改 golden 並說明。
import csv, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, unittest

HERE = pathlib.Path(__file__).resolve().parent
MEDIA = HERE / 'vci_media.py'
CHECK = HERE / 'vci_check.py'
LEDGER = HERE.parents[1] / 'miko-core' / 'scripts' / 'read_ledger.py'
FIX = HERE / 'fixtures'
HAS_FF = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))


# 提案替換稿：取代正式路徑 skills/visual-content-intelligence/scripts/test_vci.py
# 目的：所有子程序都有上限；逾時時以明確測試錯誤結束，不讓 CI 無限等待。
PYTHON_TIMEOUT_S = 60
FFMPEG_TIMEOUT_S = 120


class CommandTimeoutError(RuntimeError):
    """子程序逾時；讓 unittest 將它記為 ERROR，而不是讓 CI 無限等待。"""


def _run_process(args, *pargs, **kwargs):
    command = [str(x) for x in args]
    executable = pathlib.Path(command[0]).name if command else ''
    default_timeout = FFMPEG_TIMEOUT_S if executable in {'ffmpeg', 'ffprobe'} else PYTHON_TIMEOUT_S
    kwargs.setdefault('timeout', default_timeout)
    try:
        return subprocess.run(args, *pargs, **kwargs)
    except subprocess.TimeoutExpired as exc:
        rendered = ' '.join(command[:4])
        raise CommandTimeoutError(
            f'子程序逾時（{kwargs["timeout"]} 秒）：{rendered}'
        ) from exc


def run(*a):
    r = _run_process([sys.executable, '-I', '-B', *map(str, a)], capture_output=True, text=True)
    return r.returncode, r.stdout


def base_analysis():
    return {'source': {'file': 'demo.mp4', 'sha256': 'a' * 64, 'retrieved': '2026-11-08'},
            'request_mode': 'content_and_miko', 'complete': False,
            'media': {'kind': 'video', 'streams': {'video': 1, 'audio': 1, 'subtitle': 1}, 'frames_viewed': [1, 2, 3],
                      'audio_status': 'NOT_READ'},
            'claims': [{'id': 'C1', 'kind': 'author_claim', 'status': 'VERIFIED', 'quote': '〈作者原句〉',
                        'evidence': [{'url': 'https://example.org/doc', 'dates': '發布：UNKNOWN｜生效：UNKNOWN｜查閱：2026-11-08'}]},
                       {'id': 'C2', 'kind': 'observed', 'status': 'VERIFIED', 'locator': {'frame': 2}},
                       {'id': 'C4', 'kind': 'user_provided', 'status': 'UNVERIFIED'},
                       {'id': 'C3', 'kind': 'inference', 'status': 'INFERENCE'}],
            'proposal_items': [{'id': 'P1', 'claim_ids': ['C1'], 'miko_refs': ['skills/make-skill/SKILL.md@a816be1']}]}


class Check(unittest.TestCase):
    def test_subprocess_timeout_is_enforced(self):
        with self.assertRaises(CommandTimeoutError):
            _run_process([sys.executable, '-c', 'import time; time.sleep(2)'], timeout=0.05)

    def _run(self, a, frames=(1, 2, 3, 4), src='a' * 64, probe='auto', nosrc_col=False, proposal='auto', tfile=None):
        # 影片一律帶 frames.csv（稽核 r2）、檔案來源一律帶 probe JSON（稽核 r3）；frames=None／probe=None 表示不帶
        # 有 proposal_items 或 content_and_miko 時自動依 proposal_items 寫 PROPOSAL.md（稽核 r6 M3）；tfile＝逐字稿檔路徑，帶 --transcript
        d = tempfile.mkdtemp(); p = os.path.join(d, 'a.json')
        if frames is not None and isinstance(a.get('media'), dict): a['media'].setdefault('frames_total', len(frames))
        json.dump(a, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        args = [CHECK, p]
        if probe is not None:
            md = a.get('media') or {}
            pj = {'status': 'OK', 'file': os.path.basename(str((a.get('source') or {}).get('file', ''))), 'sha256': 'a' * 64, 'kind': md.get('kind'), 'streams': md.get('streams'), 'duration_s': 6.0 if md.get('kind') == 'video' else None} if probe == 'auto' else probe
            pp = os.path.join(d, 'probe.json'); json.dump(pj, open(pp, 'w', encoding='utf-8')); args += ['--probe', pp]
        if frames is not None:
            fp = os.path.join(d, 'frames.csv')
            with open(fp, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f); w.writerow(['idx', 't_sec', 'file', 'sha256'] + ([] if nosrc_col else ['source_sha256']))
                for i in frames: w.writerow([i, i - 1, f'f_{i:04d}.png', 'x'] + ([] if nosrc_col else [src]))
            args += ['--frames', fp]
        if proposal == 'auto' and (a.get('proposal_items') or a.get('request_mode') == 'content_and_miko'):
            proposal = '# 提案\n' + ''.join(f"## {x.get('id')} 例\n內容\n" for x in a.get('proposal_items') or [] if isinstance(x, dict))
        if isinstance(proposal, str) and proposal != 'auto':
            pm = os.path.join(d, 'PROPOSAL.md'); open(pm, 'w', encoding='utf-8').write(proposal); args += ['--proposal', pm]
        if tfile: args += ['--transcript', tfile]
        return run(*args)

    def test_ok(self):  # 正常題
        rc, out = self._run(base_analysis(), frames=[1, 2, 3, 4])
        self.assertEqual(rc, 0, out); self.assertIn('影格覆蓋 3/4', out)

    def test_complete_but_partial(self):  # 只看 3/4 張卻宣稱完整
        a = base_analysis(); a['complete'] = True
        rc, out = self._run(a, frames=[1, 2, 3, 4]); self.assertEqual(rc, 1); self.assertIn('K2', out)

    def test_unviewed_frame(self):  # 描述沒看過的影格
        a = base_analysis(); a['claims'][1]['locator'] = {'frame': 4}
        rc, out = self._run(a, frames=[1, 2, 3, 4]); self.assertEqual(rc, 1); self.assertIn('沒看過的畫面', out)

    def test_audio_guess(self):  # 有音軌沒逐字稿卻沒標 NOT_READ
        a = base_analysis(); a['media']['audio_status'] = 'OK'
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('K3', out)

    def test_inference_verified(self):  # 推論冒充已證實
        a = base_analysis(); a['claims'][2]['status'] = 'VERIFIED'
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('C3', out)

    def test_observed_bad_status(self):  # 畫面主張標 CONTRADICTED 等不合語意的狀態（T-V13 實跑發現的缺口）
        a = base_analysis(); a['claims'][1]['status'] = 'UNVERIFIED'
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('畫面主張', out)

    def test_user_provided_ok(self):  # 使用者轉述的資訊另成一類（T-V3 實跑發現的缺口）
        a = base_analysis(); a['claims'][2]['status'] = 'VERIFIED'
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('evidence', out)

    def test_verified_no_dates(self):  # 證實但缺日期一行
        a = base_analysis(); a['claims'][0]['evidence'][0]['dates'] = '查閱 2026-11-08'
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('日期一行', out)

    def test_output_only(self):  # 建議沒有來源主張（反向覆蓋）
        a = base_analysis(); a['proposal_items'].append({'id': 'P2', 'claim_ids': ['C9'], 'miko_refs': ['x']})
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('OUTPUT_ONLY', out)

    def test_no_miko_refs(self):  # 沒讀 MIKO 檔就提建議
        a = base_analysis(); a['proposal_items'][0]['miko_refs'] = []
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('miko_refs', out)

    def test_content_only(self):  # 相近反例：只問內容卻展開工程建議（T-V2 程式面）
        a = base_analysis(); a['request_mode'] = 'content_only'
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('K6', out)

    def test_video_without_frames(self):  # 稽核 r2 最強反例：影片不帶 --frames 描述第 999 張
        a = base_analysis(); a['claims'][1]['locator'] = {'frame': 999}
        rc, out = self._run(a, frames=None); self.assertEqual(rc, 1); self.assertIn('--frames', out); self.assertIn('沒看過的畫面', out)

    def test_frames_from_other_video(self):  # 稽核 r2 次要反例：拿別支影片或自製的一列 frames.csv
        a = base_analysis(); a['complete'] = True; a['media']['frames_viewed'] = [1]; a['claims'][1]['locator'] = {'frame': 1}
        rc, out = self._run(a, frames=[1], src='b' * 64); self.assertEqual(rc, 1); self.assertIn('source_sha256', out)
        a = base_analysis(); a['media']['frames_total'] = 9
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('frames_total', out)

    def test_media_kind_bypass(self):  # 稽核 r3 a3／a4／a13：省略或改寫 media.kind 繞過 --frames
        for mut in ('del', 'Video', 'nomedia'):
            a = base_analysis(); a['claims'][1]['locator'] = {'t_sec': 999}
            if mut == 'del': del a['media']['kind']
            elif mut == 'Video': a['media']['kind'] = 'Video'
            else: del a['media']
            rc, out = self._run(a, frames=None, probe=None); self.assertEqual(rc, 1, mut); self.assertIn('K2', out)

    def test_kind_vs_probe(self):  # 稽核 r3 a5：影片自稱 image；探測結果為準
        a = base_analysis(); a['media']['kind'] = 'image'; a['media']['frames_viewed'] = []; a['complete'] = True
        a['claims'][1]['locator'] = {'region': '整部影片'}
        rc, out = self._run(a, frames=None, probe={'sha256': 'a' * 64, 'kind': 'video'}); self.assertEqual(rc, 1); self.assertIn('probe 判定', out)
        a = base_analysis(); rc, out = self._run(a, probe=None); self.assertEqual(rc, 1); self.assertIn('--probe', out)
        rc, out = self._run(base_analysis(), probe={'sha256': 'b' * 64, 'kind': 'video'}); self.assertEqual(rc, 1); self.assertIn('探測的不是這個檔', out)

    def test_video_region_only(self):  # 稽核 r3 a6：影片只寫 region「第 40 分鐘」
        a = base_analysis(); a['claims'][1]['locator'] = {'region': '第 40 分鐘'}
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('frame 或 t_sec', out)

    def test_frame_and_t_sec(self):  # 稽核 r3 a7：frame 2 對、t_sec 999 錯
        a = base_analysis(); a['claims'][1]['locator'] = {'frame': 2, 't_sec': 999}
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('t_sec', out)
        a = base_analysis(); a['claims'][1]['locator'] = {'frame': 2, 't_sec': 1}
        rc, out = self._run(a); self.assertEqual(rc, 0, out)

    def test_frames_csv_no_source_col(self):  # 稽核 r3 a10：frames.csv 沒有 source_sha256 欄
        rc, out = self._run(base_analysis(), nosrc_col=True); self.assertEqual(rc, 1); self.assertIn('缺 source_sha256', out)

    def test_author_claim_unviewed_frame(self):  # 稽核 r3 a11：沒看過的畫面文字改標 author_claim
        a = base_analysis(); a['claims'][0]['locator'] = {'frame': 999}
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('沒看過的畫面', out)

    def test_url_only(self):  # 稽核 r3：只有網址的合法出口
        a = base_analysis(); a['source'] = {'url': 'https://example.org/v', 'retrieved': '2026-11-09'}
        a['media'] = {'kind': 'url_only', 'frames_viewed': [], 'audio_status': 'NOT_READ'}
        del a['claims'][1]
        rc, out = self._run(a, frames=None, probe=None); self.assertEqual(rc, 0, out)
        a['media']['kind'] = 'video'
        rc, out = self._run(a, frames=None, probe=None); self.assertEqual(rc, 1); self.assertIn('url_only', out)
        a['media']['kind'] = 'url_only'; a['claims'].append({'id': 'C9', 'kind': 'observed', 'status': 'VERIFIED', 'locator': {'region': '封面'}})
        rc, out = self._run(a, frames=None, probe=None); self.assertEqual(rc, 1); self.assertIn('不得有 observed', out)

    def test_t_sec_without_frames(self):  # 稽核 r3：沒帶 --frames 卻寫 t_sec
        a = base_analysis(); a['media']['kind'] = 'image'; a['media']['frames_viewed'] = []; a['claims'][1]['locator'] = {'t_sec': 3}
        rc, out = self._run(a, frames=None); self.assertEqual(rc, 1); self.assertIn('沒帶 --frames', out)

    def test_streams_vs_probe(self):  # 稽核 r4 最強反例：刪掉或改小 media.streams 繞過 K3
        pr = {'status': 'OK', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'kind': 'video', 'streams': {'video': 1, 'audio': 1, 'subtitle': 1}, 'duration_s': None}
        for mut in ('del', 'zero'):
            a = base_analysis(); a['media']['audio_status'] = 'OK'
            if mut == 'del': del a['media']['streams']
            else: a['media']['streams'] = {'video': 1, 'audio': 0, 'subtitle': 1}
            rc, out = self._run(a, probe=pr); self.assertEqual(rc, 1, mut); self.assertIn('K3', out)
        rc, out = self._run(base_analysis(), probe={'status': 'OK', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'kind': 'video'})
        self.assertEqual(rc, 1); self.assertIn('probe JSON 不完整', out)

    def test_probe_not_run(self):  # 稽核 r4：沒有 ffprobe 時圖片的出口是 NOT_RUN（rc=4），不是 FAIL 也不是 PASS
        a = base_analysis(); a['media'] = {'kind': 'image', 'frames_viewed': [], 'streams': {}, 'audio_status': 'NOT_READ'}
        a['claims'][1]['locator'] = {'region': '整張'}
        nr = {'status': 'NOT_RUN', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'bytes': 1}
        rc, out = self._run(a, frames=None, probe=nr); self.assertEqual(rc, 4, out); self.assertTrue(out.strip().splitlines()[-1].startswith('NOT_RUN'), out)
        a['request_mode'] = 'x'
        rc, out = self._run(a, frames=None, probe=nr); self.assertEqual(rc, 1)

    def test_frame_density(self):  # 稽核 r4 建議：120 秒影片只抽 1 張
        a = base_analysis(); a['media']['frames_viewed'] = [1]; a['claims'][1]['locator'] = {'frame': 1}
        pr = {'status': 'OK', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'kind': 'video', 'streams': a['media']['streams'], 'duration_s': 120.0}
        rc, out = self._run(a, frames=[1], probe=pr); self.assertEqual(rc, 1); self.assertIn('預設密度', out)
        a['media']['sparse_reason'] = '使用者只要封面與結尾'
        rc, out = self._run(a, frames=[1], probe=pr); self.assertEqual(rc, 0, out)
        a['complete'] = True   # 稽核 r10 建議：抽格較疏卻宣稱完整
        rc, out = self._run(a, frames=[1], probe=pr); self.assertEqual(rc, 1, out); self.assertIn('sparse_reason', out)

    def test_request_mode_missing(self):  # 稽核 r1：拿掉 request_mode 就繞過 K6
        a = base_analysis(); del a['request_mode']
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('request_mode', out)

    def test_t_sec_unviewed(self):  # 稽核 r1：用 t_sec 描述沒看過的時間點
        a = base_analysis(); a['claims'][1]['locator'] = {'t_sec': 3}
        rc, out = self._run(a, frames=[1, 2, 3, 4]); self.assertEqual(rc, 1); self.assertIn('t_sec', out)
        a = base_analysis(); a['claims'][1]['locator'] = {'t_sec': 1}
        rc, out = self._run(a, frames=[1, 2, 3, 4]); self.assertEqual(rc, 0, out)

    def test_miko_refs_no_commit(self):  # 稽核 r1：miko_refs 隨便寫一個字也能過
        a = base_analysis(); a['proposal_items'][0]['miko_refs'] = ['x']
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('路徑@commit', out)

    def test_evidence_malformed(self):  # 稽核 r1：evidence 不是物件時要 FAIL，不得 traceback
        a = base_analysis(); a['claims'][0]['evidence'] = ['https://example.org']
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertNotIn('Traceback', out)
        a = base_analysis(); a['claims'] = ['C1']
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('K0', out)

    def test_proposal_md(self):  # 稽核 r1：PROPOSAL.md 多出沒來源的 P2
        d = tempfile.mkdtemp(); pm = os.path.join(d, 'PROPOSAL.md'); ap = os.path.join(d, 'a.json')
        json.dump(base_analysis(), open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
        open(pm, 'w', encoding='utf-8').write('# 提案\n## P1 例\n內容\n## P2 沒來源\n內容\n')
        fx = ['--frames', FIX / 'ok_frames.csv', '--probe', FIX / 'ok_probe.json']
        a = base_analysis(); a['media']['frames_total'] = 4
        json.dump(a, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
        rc, out = run(CHECK, ap, '--proposal', pm, *fx); self.assertEqual(rc, 1); self.assertIn('K7 OUTPUT_ONLY', out)
        open(pm, 'w', encoding='utf-8').write('# 提案\n## P1 例\n內容\n')
        rc, out = run(CHECK, ap, '--proposal', pm, *fx); self.assertEqual(rc, 0, out)

    def test_transcript_structured(self):  # 稽核 r5 N1：transcript 隨便寫字串或寫 subs 但沒有字幕軌，就繞過 K3
        pr = {'status': 'OK', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'kind': 'video', 'streams': {'video': 1, 'audio': 1, 'subtitle': 0}, 'duration_s': None}
        for t in ('x', {'source': 'subs.srt'}, {'type': 'subs', 'file': 's.srt', 'sha256': 'b' * 64}, {'type': 'user_file', 'file': 't.txt', 'sha256': 'zz'}):
            a = base_analysis(); a['media']['streams'] = pr['streams']; a['media']['audio_status'] = 'OK'; a['transcript'] = t
            rc, out = self._run(a, probe=pr); self.assertEqual(rc, 1, (t, out)); self.assertIn('K3', out)
        d = tempfile.mkdtemp(); srt = os.path.join(d, 's.srt'); open(srt, 'w', encoding='utf-8').write('1\n00:00:00,000 --> 00:00:01,000\n〈佔位〉\n')
        h = hashlib.sha256(open(srt, 'rb').read()).hexdigest()
        for ty in ('user_file', 'subs'):
            a = base_analysis(); a['media']['audio_status'] = 'OK'; a['transcript'] = {'type': ty, 'file': 's.srt', 'sha256': h}
            rc, out = self._run(a, tfile=srt); self.assertEqual(rc, 0, (ty, out))
            a['transcript']['sha256'] = 'c' * 64
            rc, out = self._run(a, tfile=srt); self.assertEqual(rc, 1, out); self.assertIn('--transcript', out)

    def test_locator_all_kinds(self):  # 稽核 r5 N2（t3）：user_provided、inference 帶沒看過的 frame／t_sec 也要 FAIL
        a = base_analysis(); a['claims'][2]['locator'] = {'frame': 999, 't_sec': 2400}; a['claims'][3]['locator'] = {'frame': 999}
        rc, out = self._run(a); self.assertEqual(rc, 1); self.assertIn('C4', out); self.assertIn('C3', out)
        a = base_analysis(); a['media']['kind'] = 'image'; a['media']['frames_viewed'] = []; a['claims'][1]['locator'] = {'region': '整張'}
        a['claims'][3]['locator'] = {'t_sec': 5}
        rc, out = self._run(a, frames=None); self.assertEqual(rc, 1); self.assertIn('沒帶 --frames', out)

    def test_proposal_ids_anywhere(self):  # 稽核 r5 N3：P9 寫在內文、不是標題，也要對帳
        d = tempfile.mkdtemp(); pm = os.path.join(d, 'PROPOSAL.md'); ap = os.path.join(d, 'a.json')
        a = base_analysis(); a['media']['frames_total'] = 4
        json.dump(a, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
        open(pm, 'w', encoding='utf-8').write('# 提案\n## P1 例\n另外建議 P9：改 MP4 規則；**P10** 也要做\n')
        fx = ['--frames', FIX / 'ok_frames.csv', '--probe', FIX / 'ok_probe.json']
        rc, out = run(CHECK, ap, '--proposal', pm, *fx); self.assertEqual(rc, 1); self.assertIn('P9', out); self.assertIn('P10', out)

    def test_media_probe_no_ffprobe(self):  # 稽核 r5 建議：PATH 裡沒有 ffprobe 時 probe 印 NOT_RUN＋sha256，結束碼 4
        d = tempfile.mkdtemp(); f = os.path.join(d, 'x.png'); open(f, 'wb').write(b'not really a png')
        r = _run_process([sys.executable, '-I', '-B', str(MEDIA), 'probe', f], capture_output=True, text=True, env={'PATH': d})
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr); j = json.loads(r.stdout)
        self.assertEqual(j['status'], 'NOT_RUN'); self.assertEqual(j['sha256'], hashlib.sha256(b'not really a png').hexdigest())
        r = _run_process([sys.executable, '-I', '-B', str(MEDIA), 'frames', f, '--every', '2', '--out', d], capture_output=True, text=True, env={'PATH': d})
        self.assertEqual(r.returncode, 4); self.assertIn('NOT_RUN', r.stdout)

    def test_transcript_needs_file(self):  # 稽核 r6 M4：transcript 手填 64 位 hex、不帶 --transcript 就算有逐字稿
        for ty in ('subs', 'user_file'):
            a = base_analysis(); a['media']['audio_status'] = 'OK'; a['transcript'] = {'type': ty, 'file': 's.srt', 'sha256': 'b' * 64}
            rc, out = self._run(a); self.assertEqual(rc, 1, (ty, out)); self.assertIn('--transcript', out)

    def test_complete_not_bool(self):  # 稽核 r6 M1：complete 寫 1 或 "true" 繞過 K2
        for v in (1, 'true'):
            a = base_analysis(); a['complete'] = v
            rc, out = self._run(a); self.assertEqual(rc, 1, (v, out)); self.assertIn('complete', out)

    def test_video_duration_unknown(self):  # 稽核 r6 M2：probe 長度 null 或缺，抽格密度就整段不核
        for dur in (None, 'del'):
            a = base_analysis(); a['complete'] = True; a['media']['frames_viewed'] = [1]; a['claims'][1]['locator'] = {'frame': 1}
            pr = {'status': 'OK', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'kind': 'video', 'streams': a['media']['streams'], 'duration_s': dur}
            if dur == 'del': del pr['duration_s']
            rc, out = self._run(a, frames=[1], probe=pr); self.assertEqual(rc, 1, (dur, out)); self.assertIn('長度', out)
            a['media']['sparse_reason'] = '使用者只要封面'
            rc, out = self._run(a, frames=[1], probe=pr); self.assertEqual(rc, 0, out)

    def test_proposal_required_and_headings(self):  # 稽核 r6 M3：有 proposal_items 卻不帶 --proposal；全形Ｐ２、「提案二」標題
        rc, out = self._run(base_analysis(), proposal=None); self.assertEqual(rc, 1, out); self.assertIn('--proposal', out)
        for md in ('# 提案\n## P1 ok\n## Ｐ2 額外建議\n', '# 提案\n## P1 ok\n## 提案二：新增 Skill\n'):
            rc, out = self._run(base_analysis(), proposal=md); self.assertEqual(rc, 1, (md, out)); self.assertIn('K7', out)
        a = base_analysis(); a['proposal_items'] = []
        rc, out = self._run(a, proposal=None); self.assertEqual(rc, 1, out); self.assertIn('--proposal', out)

    def test_url_only_audio(self):  # 稽核 r6 M5：只有網址卻寫 audio_status OK
        a = {'source': {'url': 'https://example.org/v', 'retrieved': '2026-11-08'}, 'request_mode': 'content_only', 'complete': False,
             'media': {'kind': 'url_only', 'audio_status': 'OK'}, 'claims': [], 'proposal_items': []}
        rc, out = self._run(a, frames=None, probe=None); self.assertEqual(rc, 1, out); self.assertIn('audio_status', out)
        a['media']['audio_status'] = 'NOT_READ'
        rc, out = self._run(a, frames=None, probe=None); self.assertEqual(rc, 0, out)

    def test_claim_id_and_date(self):  # 稽核 r6 建議：claim 沒有 id、日期 2026-99-99
        a = base_analysis(); del a['claims'][0]['id']; a['proposal_items'][0]['claim_ids'] = [None]
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('id', out)
        a = base_analysis(); a['source']['retrieved'] = '2026-99-99'
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('retrieved', out)

    def test_transcript_not_source(self):  # 稽核 r7 N1：逐字稿指向來源影片本身、空檔、檔名不符、subs 不是字幕
        d = tempfile.mkdtemp(); vid = os.path.join(d, 'demo.mp4'); open(vid, 'wb').write(b'\xff\xfe\x00video')
        emp = os.path.join(d, 'empty.txt'); open(emp, 'wb').close()
        txt = os.path.join(d, 't.txt'); open(txt, 'w', encoding='utf-8').write('講者說〈佔位〉\n')
        sha = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
        cases = [({'type': 'user_file', 'file': 'demo.mp4', 'sha256': 'a' * 64}, vid, '來源'),   # sha 等於 source.sha256
                 ({'type': 'user_file', 'file': 'demo.mp4', 'sha256': sha(vid)}, vid, 'UTF-8'),
                 ({'type': 'user_file', 'file': 'empty.txt', 'sha256': sha(emp)}, emp, '空'),
                 ({'type': 'user_file', 'file': 'other.txt', 'sha256': sha(txt)}, txt, '檔名'),
                 ({'type': 'subs', 'file': 't.txt', 'sha256': sha(txt)}, txt, '-->')]
        for t, f, word in cases:
            a = base_analysis(); a['media']['audio_status'] = 'OK'; a['transcript'] = t
            rc, out = self._run(a, tfile=f); self.assertEqual(rc, 1, (t, out)); self.assertIn(word, out)
        a = base_analysis(); a['media']['audio_status'] = 'OK'; a['transcript'] = {'type': 'user_file', 'file': 't.txt', 'sha256': sha(txt)}
        rc, out = self._run(a, tfile=txt); self.assertEqual(rc, 0, out)

    def test_source_substitution(self):  # 稽核 r7 N2：source.file 寫 A 片，probe／frames 是 B 片的真實輸出
        a = base_analysis()
        pr = {'status': 'OK', 'file': 'short.mp4', 'sha256': 'a' * 64, 'kind': 'video', 'streams': a['media']['streams'], 'duration_s': 6.0}
        rc, out = self._run(a, probe=pr); self.assertEqual(rc, 1, out); self.assertIn('probe 的 file', out)
        del pr['file']; rc, out = self._run(a, probe=pr); self.assertEqual(rc, 1, out); self.assertIn('probe 的 file', out)

    def test_proposal_heading_variants(self):  # 稽核 r7 N3：行首空白、tab、setext、同編號重複
        for md in ('# 提案\n## P1 ok\n ## 提案二\n', '# 提案\n## P1 ok\n##\t提案二\n', '# 提案\n## P1 ok\n\n提案二\n------\n',
                   '# 提案\n## P1 ok\n內容\n## P1 另一個\n內容\n'):
            rc, out = self._run(base_analysis(), proposal=md); self.assertEqual(rc, 1, (md, out)); self.assertIn('K7', out)
        rc, out = self._run(base_analysis(), proposal='# 提案\n## P1 ok\n### 細節\n- 一\n\n---\n'); self.assertEqual(rc, 0, out)

    def test_r7_suggestions(self):  # 稽核 r7 建議：evidence 日期 2026-99-99、url 非 http、sparse_reason 只有空白、image／video 不寫 complete
        a = base_analysis(); a['claims'][0]['evidence'][0]['dates'] = '發布：UNKNOWN｜生效：UNKNOWN｜查閱：2026-99-99'
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('evidence', out)
        a = base_analysis(); a['claims'][0]['evidence'][0]['url'] = 'javascript:x'
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('evidence', out)
        a = base_analysis(); a['media']['frames_viewed'] = [1]; a['claims'][1]['locator'] = {'frame': 1}; a['media']['sparse_reason'] = ' '
        pr = {'status': 'OK', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'kind': 'video', 'streams': a['media']['streams'], 'duration_s': 120.0}
        rc, out = self._run(a, frames=[1], probe=pr); self.assertEqual(rc, 1, out); self.assertIn('密度', out)
        a = base_analysis(); del a['complete']
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('complete', out)

    def test_transcript_other_inputs(self):  # 稽核 r8 M1：逐字稿指向同一次呼叫的 analysis.json／probe／frames，或只有空白
        d = tempfile.mkdtemp(); sha = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
        ws = os.path.join(d, 'ws.txt'); open(ws, 'w', encoding='utf-8').write(' \n\u3000\n')
        a = base_analysis(); a['media']['audio_status'] = 'OK'; a['transcript'] = {'type': 'user_file', 'file': 'ws.txt', 'sha256': sha(ws)}
        rc, out = self._run(a, tfile=ws); self.assertEqual(rc, 1, out); self.assertIn('空', out)
        a = base_analysis(); a['media']['frames_total'] = 4; a['media']['audio_status'] = 'OK'
        for name, f in (('probe', FIX / 'ok_probe.json'), ('frames', FIX / 'ok_frames.csv'), ('proposal', FIX / 'ok_PROPOSAL.md')):
            a['transcript'] = {'type': 'user_file', 'file': os.path.basename(str(f)), 'sha256': sha(f)}
            ap = os.path.join(d, 'a.json'); json.dump(a, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
            rc, out = run(CHECK, ap, '--probe', FIX / 'ok_probe.json', '--frames', FIX / 'ok_frames.csv', '--proposal', FIX / 'ok_PROPOSAL.md', '--transcript', f)
            self.assertEqual(rc, 1, (name, out)); self.assertIn('同一次呼叫', out)
        # analysis.json 自己：先寫一份不含 transcript 的檔當逐字稿，再寫內容相同的 analysis.json
        b = base_analysis(); b['media']['frames_total'] = 4; b['media']['audio_status'] = 'OK'
        same = os.path.join(d, 'self.json'); json.dump(b, open(same, 'w', encoding='utf-8'), ensure_ascii=False)
        b['transcript'] = {'type': 'user_file', 'file': 'self.json', 'sha256': sha(same)}   # 指向另一份 analysis 樣的 JSON
        ap = os.path.join(d, 'b.json'); json.dump(b, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
        rc, out = run(CHECK, ap, '--probe', FIX / 'ok_probe.json', '--frames', FIX / 'ok_frames.csv', '--proposal', FIX / 'ok_PROPOSAL.md', '--transcript', same)
        self.assertEqual(rc, 1, out); self.assertIn('JSON', out)
        rc, out = run(CHECK, same, '--probe', FIX / 'ok_probe.json', '--frames', FIX / 'ok_frames.csv', '--proposal', FIX / 'ok_PROPOSAL.md', '--transcript', same)
        self.assertEqual(rc, 1, out)

    def test_r8_suggestions(self):  # 稽核 r8 建議：未來日期、url_only 的 url 非 http、id 多空白、PROPOSAL.md 有 BOM
        a = base_analysis(); a['source']['retrieved'] = '2099-01-01'
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('retrieved', out)
        a = base_analysis(); a['claims'][0]['evidence'][0]['dates'] = '發布：UNKNOWN｜生效：UNKNOWN｜查閱：2099-01-01'
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('evidence', out)
        u = {'source': {'url': 'x', 'retrieved': '2026-11-08'}, 'request_mode': 'content_only', 'complete': False,
             'media': {'kind': 'url_only', 'audio_status': 'NOT_READ'}, 'claims': [], 'proposal_items': []}
        rc, out = self._run(u, frames=None, probe=None); self.assertEqual(rc, 1, out); self.assertIn('url', out)
        a = base_analysis(); a['claims'][3]['id'] = 'C1 '
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('重複', out)
        rc, out = self._run(base_analysis(), proposal='\ufeff## 偷渡\n## P1 ok\n'); self.assertEqual(rc, 1, out); self.assertIn('K7', out)

    def test_audio_not_read_complete(self):  # 稽核 r13 建議：純音訊 audio_status NOT_READ 卻寫 complete true
        a = base_analysis(); a['media'] = {'kind': 'audio', 'streams': {'video': 0, 'audio': 1, 'subtitle': 0}, 'audio_status': 'NOT_READ', 'frames_viewed': []}
        a['claims'] = [{'id': 'C1', 'kind': 'inference', 'status': 'INFERENCE'}]; a['proposal_items'] = []; a['request_mode'] = 'content_only'; a['complete'] = True
        rc, out = self._run(a, frames=None); self.assertEqual(rc, 1, out); self.assertIn('complete', out)
        a['complete'] = False; rc, out = self._run(a, frames=None); self.assertEqual(rc, 0, out)

    def test_frames_not_read_exit(self):  # 稽核 r15 M1：抽格失敗（動態 WebP 結束碼 3）照 S3 改看第一張，要有不是 PASS 也不是 FAIL 的出口
        a = base_analysis(); a['complete'] = False; a['proposal_items'] = []; a['request_mode'] = 'content_only'
        a['media'].update({'frames_status': 'NOT_READ', 'frames_reason': 'vci_media frames 結束碼 3（動態 WebP 解不開）', 'frames_viewed': []})
        a['claims'] = [{'id': 'C1', 'kind': 'observed', 'status': 'VERIFIED', 'locator': {'region': '第一張整張'}}]
        rc, out = self._run(a, frames=None); self.assertEqual(rc, 4, out); self.assertTrue(out.strip().splitlines()[-1].startswith('NOT_READ'), out)
        a['complete'] = True; rc, out = self._run(a, frames=None); self.assertEqual(rc, 1, out)
        a['complete'] = False; a['media']['frames_reason'] = ' '; rc, out = self._run(a, frames=None); self.assertEqual(rc, 1, out)
        a['media']['frames_reason'] = '結束碼 3'; rc, out = self._run(a); self.assertEqual(rc, 1, out)   # 寫 NOT_READ 又帶 --frames 互相矛盾

    def test_r9_suggestions(self):  # 稽核 r9 乙／丙類補強：BOM／零寬逐字稿、本 Skill 自產檔、vci_check 輸出、id 全形與零寬、H1 與圍欄
        d = tempfile.mkdtemp(); sha = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
        def tr(name, data):
            f = os.path.join(d, name); open(f, 'wb').write(data)
            a = base_analysis(); a['media']['audio_status'] = 'OK'; a['transcript'] = {'type': 'user_file', 'file': name, 'sha256': sha(f)}
            return self._run(a, tfile=f)
        for name, data in (('bom.txt', '\ufeff'.encode()), ('zw.txt', '\u200b\u200b\n'.encode()),
                           ('pj.txt', '\ufeff{"status": "OK"}'.encode()), ('ANALYSIS.md', '講者〈佔位〉'.encode()),
                           ('out.txt', 'INFO K2 影格覆蓋 3/4\nPASS\n'.encode())):
            rc, out = tr(name, data); self.assertEqual(rc, 1, (name, out)); self.assertIn('K3', out)
        for dup in ('Ｃ1', 'C1\u200b'):
            a = base_analysis(); a['claims'][3]['id'] = dup
            rc, out = self._run(a); self.assertEqual(rc, 1, (dup, out)); self.assertIn('重複', out)
        for md in ('# 提案\n## P1 ok\n# 另建新 Skill\n', '# 提案\n## P1 ok\n\n另建\n===\n', '# 提案\n## P1 ok\n~~~\n```\n~~~\n## 偷渡\n'):
            rc, out = self._run(base_analysis(), proposal=md); self.assertEqual(rc, 1, (md, out)); self.assertIn('K7', out)
        rc, out = self._run(base_analysis(), proposal='# 提案\n## P1 ok\n```\n## 範例（圍欄內不算）\n```\n'); self.assertEqual(rc, 0, out)

    def test_author_claim_no_source(self):  # 稽核 r9 丙類（T-V11 forbidden）：沒有逐字稿時「講者在 0:12 說…」沒有定位也沒有來源
        a = base_analysis(); a['claims'].append({'id': 'C5', 'kind': 'author_claim', 'status': 'UNVERIFIED', 'quote': '講者在 0:12 說〈佔位〉'})
        rc, out = self._run(a); self.assertEqual(rc, 1, out); self.assertIn('C5', out)
        for ev in ('影片 0:12 講者口述', [{}], [{'dates': '發布：UNKNOWN｜生效：UNKNOWN｜查閱：2026-11-08'}], 'x'):   # 稽核 r10 M1
            a['claims'][-1]['evidence'] = ev
            rc, out = self._run(a); self.assertEqual(rc, 1, (ev, out)); self.assertIn('C5', out)
        a['claims'][-1]['evidence'] = [{'url': 'https://example.org/page', 'dates': '發布：UNKNOWN｜生效：UNKNOWN｜查閱：2026-11-08'}]
        rc, out = self._run(a); self.assertEqual(rc, 0, out)
        del a['claims'][-1]['evidence']; a['claims'][-1]['locator'] = {'frame': 2}
        rc, out = self._run(a); self.assertEqual(rc, 0, out)

    def test_author_claim_image_and_url(self):  # 稽核 r11 M1：圖卡、只有網址的作者主張只寫 region 不得誤擋（T-V13、T-V3）
        a = base_analysis(); a['media'] = {'kind': 'image', 'frames_viewed': [], 'streams': {'video': 1, 'audio': 0, 'subtitle': 0}, 'audio_status': 'NOT_READ'}
        a['claims'] = [{'id': 'A1', 'kind': 'author_claim', 'status': 'UNVERIFIED', 'quote': '〈圖卡原句〉', 'locator': {'region': '上半部'}}]
        a['proposal_items'] = []; a['request_mode'] = 'content_only'
        rc, out = self._run(a, frames=None); self.assertEqual(rc, 0, out)
        u = {'source': {'url': 'https://example.org/post', 'retrieved': '2026-11-08'}, 'request_mode': 'content_only', 'complete': False,
             'media': {'kind': 'url_only', 'audio_status': 'NOT_READ'}, 'proposal_items': [],
             'claims': [{'id': 'A1', 'kind': 'author_claim', 'status': 'UNVERIFIED', 'quote': '〈貼文原句〉'}]}
        rc, out = self._run(u, frames=None, probe=None); self.assertEqual(rc, 0, out)
        a['media']['sparse_reason'] = '\u200b'   # 稽核 r11 建議：只有零寬字元不算理由（圖片無密度題，改測影片）
        v = base_analysis(); v['media']['frames_viewed'] = [1]; v['claims'][1]['locator'] = {'frame': 1}; v['media']['sparse_reason'] = '\u200b'
        pr = {'status': 'OK', 'file': 'demo.mp4', 'sha256': 'a' * 64, 'kind': 'video', 'streams': v['media']['streams'], 'duration_s': 120.0}
        rc, out = self._run(v, frames=[1], probe=pr); self.assertEqual(rc, 1, out); self.assertIn('密度', out)

    def test_golden(self):  # 固定預期輸出（P 步要能 diff）
        pr = ['--probe', FIX / 'ok_probe.json', '--proposal', FIX / 'ok_PROPOSAL.md']
        rc, out = run(CHECK, FIX / 'ok_analysis.json', '--frames', FIX / 'ok_frames.csv', *pr)
        self.assertEqual(rc, 0); self.assertEqual(out, (FIX / 'ok_check_expected.txt').read_text(encoding='utf-8'))
        rc, out = run(CHECK, FIX / 'bad_analysis.json', '--frames', FIX / 'ok_frames.csv', *pr)
        self.assertEqual(rc, 1); self.assertEqual(out, (FIX / 'bad_check_expected.txt').read_text(encoding='utf-8'))

    def test_consistency(self):  # 一致性：同一輸入跑兩次輸出逐字相同
        a = base_analysis()
        self.assertEqual(self._run(a, frames=[1, 2, 3]), self._run(a, frames=[1, 2, 3]))


def _chunk_sha(out):   # 稽核 r9：區塊 SHA 只在正文之後的 END 行
    end = [l for l in out.splitlines() if l.startswith('=== END CHUNK')]
    return end[-1].split('chunk_sha256=')[1].split()[0] if end and 'chunk_sha256=' in end[-1] else ''


class Ledger(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.src = os.path.join(self.d, 'src.md')
        open(self.src, 'w', encoding='utf-8').write(''.join(f'第 {i} 行 不得 例外 {i}\n' for i in range(1, 26)))
        rc, out = run(LEDGER, 'plan', self.src, '--lines', '10'); self.assertEqual(rc, 0)
        self.plan = json.loads(out)

    def _verify(self, ks, fsha=None):
        led = {'file_sha256': fsha or self.plan['file_sha256'], 'lines_per_chunk': 10, 'chunks_read': []}
        for k in ks:
            rc, out = run(LEDGER, 'show', self.src, k, '--lines', '10'); self.assertEqual(rc, 0)
            sha = _chunk_sha(out)
            led['chunks_read'].append({'k': k, 'sha256': sha})
        p = os.path.join(self.d, 'led.json'); json.dump(led, open(p, 'w'))
        rc, out = run(LEDGER, 'verify', self.src, p, '--lines', '10')
        return rc, json.loads(out)

    def test_plan(self):  # 25 行、每塊 10 行 → 3 塊，最後一塊 21-25
        self.assertEqual(self.plan['chunks_total'], 3); self.assertEqual(self.plan['chunks'][2]['start'], 21)
        self.assertEqual(self.plan['chunks'][2]['end'], 25)

    def test_full(self):
        rc, r = self._verify([1, 2, 3]); self.assertEqual(rc, 0); self.assertEqual(r['read_status'], '全文已讀')

    def test_skip_middle(self):  # 跳過中間區塊
        rc, r = self._verify([1, 3]); self.assertEqual(rc, 1); self.assertEqual(r['missing'], [2])
        self.assertEqual(r['coverage'], '2/3')

    def test_changed_after_read(self):  # 讀完後來源被改
        rc, r = self._verify([1, 2, 3], fsha='0' * 64); self.assertEqual(rc, 3); self.assertEqual(r['read_status'], 'CONFLICT')

    def test_forged_sha(self):  # 讀取帳的區塊 SHA 是編的
        led = {'file_sha256': self.plan['file_sha256'], 'lines_per_chunk': 10,
               'chunks_read': [{'k': k, 'sha256': 'f' * 64} for k in (1, 2, 3)]}
        p = os.path.join(self.d, 'led.json'); json.dump(led, open(p, 'w'))
        rc, out = run(LEDGER, 'verify', self.src, p, '--lines', '10')
        self.assertEqual(rc, 1); self.assertEqual(json.loads(out)['mismatched'], [1, 2, 3])

    def test_plan_has_no_chunk_sha(self):  # 稽核 r1 最強反例：把 plan 的值抄進讀取帳不得過
        self.assertTrue(all(set(c) == {'k', 'start', 'end'} for c in self.plan['chunks']))
        led = {'file_sha256': self.plan['file_sha256'], 'lines_per_chunk': 10,
               'chunks_read': [{'k': c['k'], 'sha256': c.get('sha256', self.plan['file_sha256'])} for c in self.plan['chunks']]}
        p = os.path.join(self.d, 'led.json'); json.dump(led, open(p, 'w'))
        rc, out = run(LEDGER, 'verify', self.src, p, '--lines', '10')
        self.assertEqual(rc, 1); self.assertEqual(json.loads(out)['read_status'], 'PARTIAL_READ')

    def test_single_chunk_copy_plan(self):  # 稽核 r3 最強反例：只有一塊時把 plan 的 file_sha256 抄成區塊 SHA
        rc, out = run(LEDGER, 'plan', self.src); pl = json.loads(out); self.assertEqual(pl['chunks_total'], 1)
        led = {'file_sha256': pl['file_sha256'], 'lines_per_chunk': 300, 'chunks_read': [{'k': 1, 'sha256': pl['file_sha256']}]}
        p = os.path.join(self.d, 'led1.json'); json.dump(led, open(p, 'w'))
        rc, out = run(LEDGER, 'verify', self.src, p); self.assertEqual(rc, 1); self.assertEqual(json.loads(out)['read_status'], 'PARTIAL_READ')
        rc, out = run(LEDGER, 'show', self.src, 1); sha = _chunk_sha(out); self.assertNotEqual(sha, pl['file_sha256'])
        led['chunks_read'] = [{'k': 1, 'sha256': sha}]; json.dump(led, open(p, 'w'))
        rc, out = run(LEDGER, 'verify', self.src, p); self.assertEqual(rc, 0, out)

    def test_malformed_ledger(self):  # 稽核 r4 建議：讀取帳格式壞掉要 NOT_READ rc=2，不得 traceback
        p = os.path.join(self.d, 'bad.json')
        for bad in ({'chunks_read': 'x'}, {'chunks_read': [{'k': [1]}]}, [1, 2], {'chunks_read': [{'k': True, 'sha256': 'x'}]}):   # k: true（稽核 r11）
            json.dump(bad, open(p, 'w')); rc, out = run(LEDGER, 'verify', self.src, p, '--lines', '10')
            self.assertEqual(rc, 2, bad); self.assertIn('NOT_READ', out); self.assertNotIn('Traceback', out)

    def test_plan_golden(self):  # 固定預期輸出
        rc, out = run(LEDGER, 'plan', FIX / 'ledger_src.md', '--lines', '10')
        self.assertEqual(rc, 0); self.assertEqual(out, (FIX / 'ledger_plan_expected.json').read_text(encoding='utf-8'))

    def test_big_file_chunked_by_chars(self):  # 稽核 r9 M1：300 行內但 50 KB 的檔不得一塊讀完；表頭不得有區塊 SHA
        big = os.path.join(self.d, 'big.md')
        open(big, 'w', encoding='utf-8').write(''.join(f'{i:03d} ' + '字' * 999 + '\n' for i in range(50)))
        rc, out = run(LEDGER, 'plan', big); pl = json.loads(out); self.assertEqual(rc, 0)
        self.assertGreaterEqual(pl['chunks_total'], 3); self.assertIn('bytes_per_chunk', pl)
        led = {'file_sha256': pl['file_sha256'], 'lines_per_chunk': 300, 'bytes_per_chunk': pl['bytes_per_chunk'], 'chunks_read': []}
        for c in pl['chunks']:
            rc, out = run(LEDGER, 'show', big, c['k']); first = out.splitlines()[0]
            self.assertNotIn('chunk_sha256', first); self.assertEqual(len(re.findall(r'[0-9a-f]{64}', first)), 1)   # 只有檔案 SHA
            self.assertLessEqual(len(out.encode('utf-8')), 25000)   # 稽核 r10：門檻看 UTF-8 bytes，不看字元數
            led['chunks_read'].append({'k': c['k'], 'sha256': _chunk_sha(out)})
        p = os.path.join(self.d, 'bl.json'); json.dump(led, open(p, 'w'))
        rc, out = run(LEDGER, 'verify', big, p); self.assertEqual(rc, 0, out)
        led['chunks_read'] = led['chunks_read'][:1]; json.dump(led, open(p, 'w'))
        rc, out = run(LEDGER, 'verify', big, p); self.assertEqual(rc, 1, out)

    def test_bytes_cap(self):  # 稽核 r10：自帶很大的 --bytes 把整份當一塊要拒絕
        rc, out = run(LEDGER, 'plan', self.src, '--bytes', '100000'); self.assertEqual(rc, 2, out)

    def test_missing_file(self):
        rc, out = run(LEDGER, 'plan', os.path.join(self.d, 'nope.md')); self.assertEqual(rc, 2); self.assertIn('NOT_READ', out)


@unittest.skipUnless(HAS_FF, 'NOT_RUN：本機沒有 ffmpeg／ffprobe')
class Media(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()
        srt = os.path.join(cls.d, 's.srt')
        open(srt, 'w', encoding='utf-8').write('1\n00:00:00,000 --> 00:00:02,000\n合成字幕〈佔位〉\n')
        cls.v = os.path.join(cls.d, 'demo.mkv'); cls.nos = os.path.join(cls.d, 'nosub.mp4'); cls.img = os.path.join(cls.d, 'still.png')
        ff = ['ffmpeg', '-v', 'error', '-nostdin', '-y']
        _run_process(ff + ['-f', 'lavfi', '-i', 'testsrc=duration=6:size=160x120:rate=10', '-f', 'lavfi', '-i', 'sine=duration=6',
                             '-i', srt, '-map', '0', '-map', '1', '-map', '2', '-c:s', 'srt', '-t', '6', cls.v], check=True)
        _run_process(ff + ['-f', 'lavfi', '-i', 'testsrc=duration=3:size=160x120:rate=10', cls.nos], check=True)
        _run_process(ff + ['-f', 'lavfi', '-i', 'testsrc=size=160x120', '-frames:v', '1', cls.img], check=True)
        cls.gif = os.path.join(cls.d, 'anim.gif'); cls.avi = os.path.join(cls.d, 'mj.avi'); cls.jpg = os.path.join(cls.d, 'still.jpg')
        _run_process(ff + ['-f', 'lavfi', '-i', 'testsrc=duration=3:size=80x60:rate=5', cls.gif], check=True)
        _run_process(ff + ['-f', 'lavfi', '-i', 'testsrc=duration=3:size=80x60:rate=5', '-c:v', 'mjpeg', cls.avi], check=True)
        _run_process(ff + ['-f', 'lavfi', '-i', 'testsrc=size=80x60', '-frames:v', '1', cls.jpg], check=True)
        cls.mka = os.path.join(cls.d, 'cover.mp3')   # 帶封面圖的 mp3（ID3 APIC，ffprobe 標 attached_pic）
        _run_process(ff + ['-i', cls.jpg, '-f', 'lavfi', '-i', 'sine=duration=2', '-map', '1', '-map', '0', '-c:a', 'libmp3lame',
                             '-c:v', 'mjpeg', '-disposition:v:0', 'attached_pic', '-id3v2_version', '3', cls.mka], check=True)

    def test_probe_video(self):
        rc, out = run(MEDIA, 'probe', self.v); j = json.loads(out)
        self.assertEqual(rc, 0); self.assertEqual(j['kind'], 'video')
        self.assertEqual(j['streams'], {'video': 1, 'audio': 1, 'subtitle': 1}); self.assertAlmostEqual(j['duration_s'], 6, delta=0.2)

    def test_media_golden(self):  # 稽核 r2：S1、S3、S4 的 P 步固定預期輸出（正規化掉會隨 ffmpeg 版本變的 SHA 與檔案大小）
        rc, out = run(MEDIA, 'probe', self.v); j = json.loads(out); self.assertEqual(rc, 0)
        norm = {k: j[k] for k in ('status', 'kind', 'width', 'height', 'streams')}; norm['duration_s'] = round(j['duration_s'])
        self.assertEqual(norm, json.loads((FIX / 'media_probe_expected.json').read_text(encoding='utf-8')))
        o = os.path.join(self.d, 'frg'); rc, _ = run(MEDIA, 'frames', self.v, '--every', '2', '--out', o); self.assertEqual(rc, 0)
        rows = list(csv.DictReader(open(os.path.join(o, 'frames.csv'), encoding='utf-8')))
        self.assertEqual({r['source_sha256'] for r in rows}, {j['sha256']})
        got = ''.join(f"{r['idx']},{r['t_sec']},{r['file']}\n" for r in rows)
        self.assertEqual(got, (FIX / 'media_frames_expected.txt').read_text(encoding='utf-8'))
        so = os.path.join(self.d, 'g.srt'); rc, _ = run(MEDIA, 'subs', self.v, '--out', so); self.assertEqual(rc, 0)
        # 時間碼會因封裝容器偏移數毫秒（實測 mkv 偏 3 ms），golden 只比編號與字幕文字，時間碼另以 ±50 ms 容差比
        import re
        lines = open(so, encoding='utf-8').read().strip().splitlines()
        tc = [l for l in lines if '-->' in l]; txt = [l for l in lines if '-->' not in l]
        self.assertEqual('\n'.join(txt) + '\n', (FIX / 'media_subs_expected.txt').read_text(encoding='utf-8'))
        ms = [int(h) * 3600000 + int(m) * 60000 + int(x) * 1000 + int(f) for h, m, x, f in re.findall(r'(\d+):(\d+):(\d+),(\d+)', tc[0])]
        self.assertEqual(len(tc), 1); self.assertLessEqual(abs(ms[0] - 0), 50); self.assertLessEqual(abs(ms[1] - 2000), 50)

    def test_probe_animated_and_silent(self):  # 稽核 r3：動態 GIF、無聲 MJPEG 影片不得判成圖片（golden）
        exp = json.loads((FIX / 'media_probe_anim_expected.json').read_text(encoding='utf-8'))
        for name in ('gif', 'avi'):
            rc, out = run(MEDIA, 'probe', getattr(self, name)); j = json.loads(out); self.assertEqual(rc, 0)
            norm = {k: j[k] for k in ('kind', 'width', 'height', 'streams')}; norm['duration_s'] = round(j['duration_s'])
            self.assertEqual(norm, exp, name)
        rc, out = run(MEDIA, 'probe', self.jpg); self.assertEqual(json.loads(out)['kind'], 'image')

    def test_probe_audio_with_cover(self):  # 稽核 r4 建議：帶封面圖的音訊判 audio
        rc, out = run(MEDIA, 'probe', self.mka); j = json.loads(out); self.assertEqual(rc, 0)
        self.assertEqual(j['kind'], 'audio'); self.assertEqual(j['streams']['video'], 0)

    def test_probe_raw_stream_duration(self):  # 稽核 r6 M2：raw H.264 容器沒有長度，probe 要補算，不得 null
        raw = os.path.join(self.d, 'raw.h264')
        _run_process(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-f', 'lavfi', '-i', 'testsrc=duration=4:size=80x60:rate=5',
                        '-c:v', 'libx264', '-f', 'h264', raw], check=True)
        rc, out = run(MEDIA, 'probe', raw); j = json.loads(out); self.assertEqual(rc, 0); self.assertEqual(j['kind'], 'video')
        self.assertIsInstance(j['duration_s'], float)

    def test_default_density_real_output(self):  # 稽核 r12 M1：照預設間隔抽格、全部看完的正確答案不得被密度檢查誤擋（真實 ffmpeg 輸出）
        for dur, every, extra in ((10.9, 2, 0), (61, 10, 0), (0.8, 2, 0), (10, 2, 1), (20, 2, 1.5)):   # extra＝音軌比影像長幾秒（稽核 r13 M1）
            v = os.path.join(self.d, f'd{dur}_{extra}.mp4')
            aud = ['-f', 'lavfi', '-i', f'sine=duration={dur + extra}', '-c:a', 'aac'] if extra else []
            _run_process(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-f', 'lavfi', '-i', f'testsrc=duration={dur}:size=64x48:rate=10', *aud, '-c:v', 'libx264', v], check=True)
            rc, out = run(MEDIA, 'probe', v); pj = json.loads(out); self.assertEqual(rc, 0)
            o = os.path.join(self.d, f'fd{dur}_{extra}'); rc, out = run(MEDIA, 'frames', v, '--every', every, '--out', o); self.assertEqual(rc, 0, (dur, out))
            rows = list(csv.DictReader(open(os.path.join(o, 'frames.csv'), encoding='utf-8'))); n = len(rows); self.assertGreaterEqual(n, 1)
            a = {'source': {'file': os.path.basename(v), 'sha256': pj['sha256'], 'retrieved': '2026-11-08'}, 'request_mode': 'content_only',
                 'complete': True, 'media': {'kind': 'video', 'streams': pj['streams'], 'frames_viewed': list(range(1, n + 1)),
                 'frames_total': n, 'audio_status': 'NOT_READ'}, 'proposal_items': [],
                 'claims': [{'id': 'C1', 'kind': 'observed', 'status': 'VERIFIED', 'locator': {'frame': 1}}]}
            ap = os.path.join(self.d, f'a{dur}_{extra}.json'); json.dump(a, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
            pp = os.path.join(self.d, f'p{dur}_{extra}.json'); json.dump(pj, open(pp, 'w', encoding='utf-8'), ensure_ascii=False)
            rc, out = run(CHECK, ap, '--probe', pp, '--frames', os.path.join(o, 'frames.csv')); self.assertEqual(rc, 0, (dur, n, out))

    def test_density_flv_wmv(self):  # 稽核 r14 M1：FLV、WMV 影像 10 秒／音軌 14 秒，照預設每 2 秒抽、全看完不得被誤擋
        for ext, codec in (('flv', ['-c:v', 'flv', '-c:a', 'libmp3lame']), ('wmv', ['-c:v', 'wmv2', '-c:a', 'wmav2'])):
            v = os.path.join(self.d, f'r.{ext}')
            _run_process(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-f', 'lavfi', '-i', 'testsrc=size=64x48:rate=10:duration=10',
                            '-f', 'lavfi', '-i', 'sine=duration=14', *codec, v], check=True)
            rc, out = run(MEDIA, 'probe', v); pj = json.loads(out); self.assertEqual(rc, 0)
            o = os.path.join(self.d, f'fr_{ext}'); rc, out = run(MEDIA, 'frames', v, '--every', 2, '--out', o); self.assertEqual(rc, 0, out)
            n = len(list(csv.DictReader(open(os.path.join(o, 'frames.csv'), encoding='utf-8'))))
            a = {'source': {'file': os.path.basename(v), 'sha256': pj['sha256'], 'retrieved': '2026-11-08'}, 'request_mode': 'content_only',
                 'complete': True, 'media': {'kind': 'video', 'streams': pj['streams'], 'frames_viewed': list(range(1, n + 1)),
                 'frames_total': n, 'audio_status': 'NOT_READ'}, 'proposal_items': [],
                 'claims': [{'id': 'C1', 'kind': 'observed', 'status': 'VERIFIED', 'locator': {'frame': 1}}]}
            ap = os.path.join(self.d, f'a_{ext}.json'); json.dump(a, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
            pp = os.path.join(self.d, f'p_{ext}.json'); json.dump(pj, open(pp, 'w', encoding='utf-8'), ensure_ascii=False)
            rc, out = run(CHECK, ap, '--probe', pp, '--frames', os.path.join(o, 'frames.csv')); self.assertEqual(rc, 0, (ext, n, pj, out))
            o2 = os.path.join(self.d, f'fr6_{ext}'); run(MEDIA, 'frames', v, '--every', 6, '--out', o2)   # 每 6 秒太疏，要 FAIL
            n2 = len(list(csv.DictReader(open(os.path.join(o2, 'frames.csv'), encoding='utf-8'))))
            a['media']['frames_viewed'] = list(range(1, n2 + 1)); a['media']['frames_total'] = n2; json.dump(a, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
            rc, out = run(CHECK, ap, '--probe', pp, '--frames', os.path.join(o2, 'frames.csv')); self.assertEqual(rc, 1, (ext, out)); self.assertIn('密度', out)

    def test_probe_image(self):
        rc, out = run(MEDIA, 'probe', self.img); self.assertEqual(rc, 0); self.assertEqual(json.loads(out)['kind'], 'image')

    def test_probe_missing(self):
        rc, out = run(MEDIA, 'probe', os.path.join(self.d, 'nope.mp4')); self.assertEqual(rc, 3); self.assertIn('NOT_READ', out)

    def test_frames_and_rerun(self):  # 每 2 秒一張 → 3 張；重跑不累加、輸出逐字相同
        o = os.path.join(self.d, 'fr')
        rc, _ = run(MEDIA, 'frames', self.v, '--every', '2', '--out', o); self.assertEqual(rc, 0)
        a = open(os.path.join(o, 'frames.csv'), encoding='utf-8').read()
        rc, _ = run(MEDIA, 'frames', self.v, '--every', '2', '--out', o); self.assertEqual(rc, 0)
        b = open(os.path.join(o, 'frames.csv'), encoding='utf-8').read()
        self.assertEqual(a, b); self.assertEqual(len(a.strip().splitlines()) - 1, 3)
        self.assertEqual(len([f for f in os.listdir(o) if f.endswith('.png')]), 3)

    def test_subs(self):
        o = os.path.join(self.d, 'out.srt')
        rc, _ = run(MEDIA, 'subs', self.v, '--out', o); self.assertEqual(rc, 0)
        self.assertIn('合成字幕', open(o, encoding='utf-8').read())

    def test_no_subs(self):  # 沒字幕軌：NOT_READ，結束碼 1
        rc, out = run(MEDIA, 'subs', self.nos, '--out', os.path.join(self.d, 'x.srt'))
        self.assertEqual(rc, 1); self.assertIn('NOT_READ', out)

    def test_source_untouched(self):  # 不改原始檔
        h = hashlib.sha256(open(self.v, 'rb').read()).hexdigest()
        run(MEDIA, 'frames', self.v, '--every', '3', '--out', os.path.join(self.d, 'fr2'))
        self.assertEqual(h, hashlib.sha256(open(self.v, 'rb').read()).hexdigest())


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    n, s = r.testsRun, len(r.skipped)
    print(f'PASS {n - s - len(r.failures) - len(r.errors)}／NOT_RUN {s}／FAIL {len(r.failures) + len(r.errors)}（共 {n} 題）')
    sys.exit(1 if not r.wasSuccessful() else 5 if s else 0)
