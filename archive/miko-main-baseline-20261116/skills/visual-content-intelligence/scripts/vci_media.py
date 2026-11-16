#!/usr/bin/env python3
# vci_media.py｜visual-content-intelligence 的媒體 P 步：探測、抽影格、抽內嵌字幕（只用標準函式庫＋ffprobe／ffmpeg）
# 用法：
#   python3 -I -B vci_media.py probe  <媒體檔>                         → 印出 JSON：SHA-256、大小、種類、長度、解析度、各類串流數
#   python3 -I -B vci_media.py frames <影片檔> --every <秒> --out <資料夾> → 每 N 秒抽一張 PNG，寫 <資料夾>/frames.csv（idx,t_sec,file,sha256,source_sha256）
#   python3 -I -B vci_media.py subs   <影片檔> --out <檔名.srt>          → 抽第一條內嵌字幕軌
# 結束碼：0＝成功；1＝沒有可抽的內容（無字幕軌：字幕 NOT_READ；不是影片）；2＝用法錯誤；3＝檔案讀不到或解不開（NOT_READ）；
#         4＝本機沒有 ffprobe／ffmpeg（NOT_RUN：不得假裝已抽影格，改請 MIKO 在有 ffmpeg 的環境跑，或只分析使用者給的截圖；probe 此時仍印 sha256 與大小）
# 重跑：frames 先清掉 <資料夾> 裡舊的 f_*.png 與 frames.csv 再寫，同一輸入同一參數重跑結果相同、不累加重複影格；不改動原始媒體檔。
# 不做：不下載網址（下載工具要先經 MIKO 批准，miko-core §6、§7）；不做語音轉文字（本 Skill 沒有配置 ASR）。
import csv, hashlib, json, os, re, shutil, subprocess, sys


def _need(tool):
    if not shutil.which(tool):
        print(json.dumps({'status': 'NOT_RUN', 'reason': f'本機沒有 {tool}'}, ensure_ascii=False)); sys.exit(4)


def _sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''): h.update(blk)
    return h.hexdigest()


def _vdur(v):
    # 影像串流本身的長度（稽核 r13：容器長度取最長串流，音軌較長時會比影格的時間軸長）；mp4 讀 duration，mkv 讀 tags.DURATION
    d = v.get('duration')
    if d not in (None, '', 'N/A'):
        try: return round(float(d), 3)
        except ValueError: pass
    t = (v.get('tags') or {}).get('DURATION') or (v.get('tags') or {}).get('duration')
    m = re.fullmatch(r'(\d+):(\d+):(\d+(?:\.\d+)?)', str(t or '').strip())
    return round(int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)), 3) if m else None


def _vdur_packets(path):
    # 稽核 r14：FLV 的影像串流沒有 duration、ASF／WMV 的影像 duration 等於容器長度，改用影像最後一個封包的結束時間扣掉起點
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'packet=pts_time,duration_time',
                        '-of', 'csv=p=0', path], capture_output=True, text=True)
    ends, starts = [], []
    for l in r.stdout.splitlines():
        p = l.strip().split(',')
        try:
            t = float(p[0]); starts.append(t); ends.append(t + (float(p[1]) if len(p) > 1 and p[1] not in ('', 'N/A') else 0))
        except (ValueError, IndexError): pass
    return round(max(ends) - min(starts), 3) if ends else None


def probe(path):
    if not os.path.isfile(path):
        print(json.dumps({'status': 'NOT_READ', 'reason': '檔案不存在'}, ensure_ascii=False)); sys.exit(3)
    if not shutil.which('ffprobe'):   # 沒有 ffprobe 仍給 SHA-256 與大小，圖片可直接看、S7 的 K1 仍能過；種類與長度 NOT_RUN
        print(json.dumps({'status': 'NOT_RUN', 'reason': '本機沒有 ffprobe：種類、長度、串流未探測', 'file': os.path.basename(path),
                          'sha256': _sha(path), 'bytes': os.path.getsize(path)}, ensure_ascii=False, indent=1)); sys.exit(4)
    r = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({'status': 'NOT_READ', 'reason': 'ffprobe 解不開：' + r.stderr.strip()[:200]}, ensure_ascii=False)); sys.exit(3)
    j = json.loads(r.stdout)
    st = j.get('streams', [])
    st = [s for s in st if not (s.get('codec_type') == 'video' and s.get('disposition', {}).get('attached_pic'))]  # 封面圖不算影像串流（稽核 r4）
    cnt = {k: sum(1 for s in st if s.get('codec_type') == k) for k in ('video', 'audio', 'subtitle')}
    v = next((s for s in st if s.get('codec_type') == 'video'), {})
    dur = j.get('format', {}).get('duration')
    fmt_name = set(str(j.get('format', {}).get('format_name', '')).split(','))
    # 靜態圖判定（稽核 r3：只看 codec 會把動態 GIF、無聲 MJPEG 影片誤判成圖片）：沒有音軌、只有一條影像串流，且實際影格數 ≤ 1
    still = False
    if cnt['video'] == 1 and not cnt['audio']:
        n = v.get('nb_frames')
        if not (n and str(n).isdigit()):
            rc = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
                                 '-of', 'csv=p=0', path], capture_output=True, text=True)
            n = rc.stdout.strip().split(',')[0] if rc.returncode == 0 else ''
        still = str(n).isdigit() and int(n) <= 1
    kind = 'image' if still else 'video' if cnt['video'] else 'audio' if cnt['audio'] else 'unknown'
    est = False
    if not dur and kind == 'video':   # 稽核 r6 M2：容器沒有長度（例如 raw H.264）時改用串流長度，再不行用實數影格數 ÷ 影格率
        dur = v.get('duration') if v.get('duration') not in (None, '', 'N/A') else None
        if not dur:
            rc = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
                                 '-of', 'csv=p=0', path], capture_output=True, text=True)
            n = rc.stdout.strip().split(',')[0] if rc.returncode == 0 else ''
            num, _, den = str(v.get('avg_frame_rate') or v.get('r_frame_rate') or '0/0').partition('/')
            try:
                fps = float(num) / float(den or 1)
                dur = int(n) / fps if n.isdigit() and fps > 0 else None
                est = dur is not None
            except (ValueError, ZeroDivisionError): dur = None
    out = {'status': 'OK', 'file': os.path.basename(path), 'sha256': _sha(path), 'bytes': os.path.getsize(path), 'kind': kind,
           'duration_s': round(float(dur), 3) if dur and dur != 'N/A' and kind != 'image' else None,
           'video_duration_s': ((_vdur_packets(path) if (fmt_name & {'flv', 'asf'}) or _vdur(v) is None else _vdur(v)) if kind == 'video' else None),
           'width': v.get('width'), 'height': v.get('height'), 'streams': cnt}
    if kind == 'video' and not (v.get('width') and v.get('height')):   # 稽核 r15：動態 WebP 等 ffmpeg 解不開的動畫，寬高回 0
        out['probe_note'] = '寬高為 0：ffmpeg 可能解不開這個動畫格式（例如動態 WebP），frames 會失敗，照 S3 失敗處理改看第一張'
    if est: out['duration_note'] = '容器沒有長度，以影格數÷影格率推估（raw 串流用 ffmpeg 預設影格率，和 frames 抽格時間軸一致；稽核 r7）'
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return out


def frames(path, every, outdir):
    _need('ffmpeg'); _need('ffprobe')
    if every <= 0:
        print('--every 要大於 0'); sys.exit(2)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if (f.startswith('f_') and f.endswith('.png')) or f == 'frames.csv': os.remove(os.path.join(outdir, f))
    r = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', path, '-vf', f'fps=1/{every}', '-map_metadata', '-1',
                        '-flags', '+bitexact', '-fflags', '+bitexact', os.path.join(outdir, 'f_%04d.png')],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({'status': 'NOT_READ', 'reason': 'ffmpeg 抽影格失敗：' + r.stderr.strip()[:200]}, ensure_ascii=False)); sys.exit(3)
    names = sorted(f for f in os.listdir(outdir) if f.startswith('f_') and f.endswith('.png'))
    if not names:   # 稽核 r12：片長短於間隔（例如 0.8 秒的 GIF）時 fps 濾鏡抽不到，改抽第一張，檔案讀得到就不算 NOT_READ
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', path, '-frames:v', '1', '-map_metadata', '-1',
                        '-flags', '+bitexact', '-fflags', '+bitexact', os.path.join(outdir, 'f_0001.png')], capture_output=True, text=True)
        names = sorted(f for f in os.listdir(outdir) if f.startswith('f_') and f.endswith('.png'))
    if not names:
        print(json.dumps({'status': 'NOT_READ', 'reason': '沒有抽到任何影格（不是影片或長度為 0）'}, ensure_ascii=False)); sys.exit(1)
    src = _sha(path)   # 每列帶原始影片 SHA，vci_check 拿來和 analysis.json 的 source.sha256 對（稽核 r2）
    with open(os.path.join(outdir, 'frames.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['idx', 't_sec', 'file', 'sha256', 'source_sha256'])
        for i, n in enumerate(names, 1):
            w.writerow([i, round((i - 1) * every, 3), n, _sha(os.path.join(outdir, n)), src])
    print(json.dumps({'status': 'OK', 'source_sha256': src, 'every_s': every, 'frames_total': len(names),
                      'csv': os.path.join(outdir, 'frames.csv')}, ensure_ascii=False, indent=1))


def subs(path, out):
    _need('ffmpeg'); _need('ffprobe')
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index', '-of', 'csv=p=0', path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({'status': 'NOT_READ', 'reason': 'ffprobe 解不開'}, ensure_ascii=False)); sys.exit(3)
    if not r.stdout.strip():
        print(json.dumps({'status': 'NOT_READ', 'reason': '沒有內嵌字幕軌；講者說的話不得憑畫面推測'}, ensure_ascii=False)); sys.exit(1)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', path, '-map', '0:s:0', out], capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({'status': 'NOT_READ', 'reason': '字幕抽取失敗：' + r.stderr.strip()[:200]}, ensure_ascii=False)); sys.exit(3)
    print(json.dumps({'status': 'OK', 'srt': out, 'sha256': _sha(out)}, ensure_ascii=False, indent=1))


def main(a):
    def opt(name):
        if name in a and a.index(name) + 1 < len(a): return a[a.index(name) + 1]
        return None
    if len(a) >= 2 and a[0] == 'probe': probe(a[1]); return 0
    if len(a) >= 2 and a[0] == 'frames' and opt('--every') and opt('--out'):
        try: ev = float(opt('--every'))
        except ValueError: print('--every 要是數字'); sys.exit(2)
        frames(a[1], ev, opt('--out')); return 0
    if len(a) >= 2 and a[0] == 'subs' and opt('--out'): subs(a[1], opt('--out')); return 0
    print('用法：probe <檔> ｜ frames <影片> --every <秒> --out <資料夾> ｜ subs <影片> --out <檔.srt>'); sys.exit(2)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
