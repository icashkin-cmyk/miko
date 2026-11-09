#!/usr/bin/env python3
# vci_check.py｜檢查 visual-content-intelligence 的 analysis.json（只用標準函式庫）
# 用法：python3 -I -B vci_check.py <analysis.json> [--probe <probe.json>] [--frames <frames.csv>] [--proposal <PROPOSAL.md>] [--transcript <字幕或逐字稿檔>]
# 檢查項（全由程式判定，模型不得自評代替）：
#   K1 來源：source 有 url 或 file；有 file 時要有 sha256；要有查閱日期 YYYY-MM-DD
#   K2 讀取範圍：有 frames.csv 時，frames_viewed 只能是 frames.csv 裡的 idx；覆蓋率由程式算；沒看完全部影格時 complete 不得為 true
#   K3 音訊：probe 顯示有音軌、但沒有逐字稿來源（transcript）時，audio_status 必須是 NOT_READ
#   K4 主張：id 不重複；kind 只能 observed（畫面看到的）／author_claim（作者說的）／user_provided（使用者本輪告訴我的）／inference（我推論的）；
#      status 只能 VERIFIED／CONTRADICTED／UNVERIFIED／INFERENCE／UNKNOWN／NOT_READ；
#      observed 要有 locator（frame 編號或時間）且引用的影格必須在 frames_viewed 裡；inference 只能標 INFERENCE 或 UNKNOWN；
#      observed 的 status 只能 VERIFIED（看得清楚，證據就是 locator）或 UNKNOWN（看不清）；
#      其他 kind 標 VERIFIED、CONTRADICTED 要有 evidence（url 與日期一行「發布：…｜生效：…｜查閱：…」）
#   K5 反向覆蓋：proposal_items 每項的 claim_ids 不得為空、且都要存在（否則 OUTPUT_ONLY）；每項要有 miko_refs（引用的 MIKO 檔案路徑）
#   K6 只問內容：request_mode 是 content_only 時 proposal_items 必須為空（使用者沒要求就不展開 MIKO 工程轉化）；
#      request_mode 必填，只能 content_only／content_and_miko（缺了不得當成「有要求」）
#   K7 提案檔對帳：有 --proposal 時，PROPOSAL.md 的標題編號（## P1 …）必須和 proposal_items 的 id 一一相同（多一個＝OUTPUT_ONLY，少一個＝漏寫）
#   K0 結構：欄位型別不對（例如 evidence 不是物件）一律 FAIL，不丟出 traceback
#   補充（稽核 r3）：media.kind 必填，只能 image／video／audio／url_only；source 有 file 時一定要帶 --probe（vci_media.py probe 的 JSON），
#      probe 的 sha256 要等於 source.sha256、kind 要等於 media.kind（種類以程式探測為準，不信手填）；url_only 只能用在沒有 file 的來源，
#      不得有 observed、complete 不得為 true；影片與音訊的 observed 要有 frame 或 t_sec（只寫 region 不算）；沒帶 --frames 卻寫 frame／t_sec 一律 FAIL；
#      frame 與 t_sec 同時寫時兩個都對；frames.csv 缺 source_sha256 欄 FAIL；author_claim 帶 frame 時也要在 frames_viewed 裡。
#   補充（稽核 r2）：影片（media.kind＝video）一定要帶 --frames；frames.csv 的 source_sha256 要等於 source.sha256，列數要等於 media.frames_total；
#      observed 的 frame 不在 frames_viewed 一律 FAIL（不論有沒有帶 --frames）。殘餘風險：整份 frames.csv 連同 SHA 自己偽造仍擋不住，驗收另看工具紀錄的 frames 呼叫。
#   補充（稽核 r1）：observed 用 t_sec 定位時，t_sec 必須等於某張已看影格的 t_sec；miko_refs 每筆要寫成 路徑@commit（7～40 位 hex）
#   補充（稽核 r4）：有 --probe 時音軌以 probe.streams 為準，media.streams 缺或和 probe 不同就 FAIL（不得靠省略欄位繞過 K3）；
#      probe 狀態 OK 卻沒有 streams 算 probe 不完整；影片抽格密度以 probe 的 duration_s 核對（短於 60 秒至少每 2 秒一張、其餘至少每 10 秒一張，
#      較疏要在 media.sparse_reason 寫理由，FAIL 改成 INFO 提示）；probe 狀態 NOT_RUN（沒有 ffprobe）時種類不核、其他照查，
#      沒有其他 FAIL 就印 NOT_RUN、結束碼 4（不算 PASS，不得改 probe.json 繞過）。
#   補充（稽核 r5）：transcript 要寫成物件 {"type": "subs"|"user_file", "file": 檔名, "sha256": 64 位 hex}；字串、缺欄位、
#      type＝subs 但 probe 顯示沒有字幕軌，一律 K3 FAIL（不得隨便寫一個字繞過 K3）；帶 --subs 時該檔 SHA-256 要等於 transcript.sha256；
#      frame／t_sec 的核對擴及所有 kind（user_provided、inference 帶 locator 時同樣要在 frames_viewed 裡、要帶 --frames）；
#      K7 對帳改抓 PROPOSAL.md 內任何位置的 P＋數字（不只標題），所以 PROPOSAL.md 不得拿 P＋數字指別的東西。
#   補充（稽核 r6）：complete 只能是 true／false（寫 1 或 "true" 算 K0 FAIL）；影片 probe OK 但 duration_s 不是數字時，
#      要寫 media.sparse_reason，否則 FAIL（長度不明無法核密度）；proposal_items 不是空的或 request_mode＝content_and_miko 時一定要帶 --proposal；
#      PROPOSAL.md 先做 NFKC 正規化（全形Ｐ２＝P2），每個「## 」標題都要是「## P數字 …」；transcript 不是空的時一定要帶 --transcript
#      （舊名 --subs 照收），該檔 SHA-256 要等於 transcript.sha256；url_only 時 audio_status 只能 NOT_READ；
#      claim id 要是非空字串；retrieved 要是真的日期（2026-99-99 不算）。
#   補充（稽核 r7）：probe.file 要等於 source.file 的檔名（不得拿別支片的真實 probe／frames 頂替）；--transcript 的檔名要等於
#      transcript.file、不得是空檔、要能用 UTF-8 解碼、sha256 不得等於 source.sha256（逐字稿不能指向影片本身），type＝subs 還要含「-->」；
#      PROPOSAL.md 的二級標題照 Markdown 判（行首 0～3 個空白、## 後接空白或 tab、setext「文字＋下一行 ---」都算），每個都要是 P＋數字，
#      同一編號只能有一個標題；evidence 日期一行整行比對且查閱日要是真日期、url 要 http(s)；sparse_reason 去掉空白後要有字；
#      image／video 一定要寫 complete。
#   補充（稽核 r8）：--transcript 的檔去掉空白後要有字，SHA-256 不得等於同一次呼叫的 analysis.json、--probe、--frames、--proposal 任一檔；
#      source.retrieved 與 evidence 的查閱日不得晚於執行當天（容許 +1 天時差，發布、生效日可在未來）；source.url 要 http(s)；
#      claim id 先去空白再比重複；PROPOSAL.md 以 utf-8-sig 讀（BOM 不藏標題）；逐字稿是 JSON 或 frames.csv 格式一律 FAIL。
#   補充（稽核 r10）：沒有逐字稿的 author_claim 若靠 evidence 過關，evidence 要和 VERIFIED 同樣合格（http(s) url＋日期一行），字串或空物件不算；
#      抽格少於預設密度（寫了 sparse_reason）時 complete 不得為 true。把講者的話改標 user_provided 程式分不出，交 S5 與稽核。
#   補充（稽核 r11）：上一條（沒有逐字稿的 author_claim）只在 media.kind 是 video／audio 且有音軌時套用；sparse_reason 去掉零寬字元後要有字。
#   補充（稽核 r12）：預設密度需要的張數＝max(1, 長度÷間隔四捨五入)，和 vci_media frames 的實際輸出一致。
#   補充（稽核 r13）：抽格密度用 probe 的 video_duration_s（影像串流長度），沒有才用 duration_s；音訊 audio_status＝NOT_READ 時 complete 不得為 true。
#   補充（稽核 r14）：抽格密度兩張以上時核 frames.csv 的間隔（t_sec 差）不得大於預設（短於 60 秒每 2 秒、其餘每 10 秒），只有一張時才核張數。
#   補充（稽核 r15）：抽格失敗（vci_media frames 結束碼 1／3，例如動態 WebP）時寫 media.frames_status＝NOT_READ 與 frames_reason、不帶 --frames、
#      complete 寫 false，observed 可只寫 region；沒有其他 FAIL 就印 NOT_READ、結束碼 4（不是 PASS 也不是 FAIL）。frames.csv 的 t_sec 從第一張影格起算（0），
#      影像晚開始的片子和播放器時間軸有落差。
#   殘餘風險（稽核 r5）：probe.json、frames.csv 都是本程式的輸入，整份連同 SHA 自己偽造仍擋不住；本程式只擋「漏填、改小、對不上」，
#      驗收另看工具紀錄裡實際的 vci_media.py probe／frames 呼叫與輸出（S7）。K7 只對帳標題與 P＋數字，寫在內文、沒有編號的建議擋不住，
#      靠 S8 人工審 PROPOSAL.md（稽核 r7）。有音軌沒逐字稿時，author_claim 掛在已看影格上，程式判不出那張畫面上有沒有那句話，交 S5 與稽核核對畫面文字（稽核 r12）。標題判定只涵蓋 ATX 與 setext 二級標題，引言內標題、HTML <h2> 不算（稽核 r8）。
#      user_file 是不是這支影片的逐字稿、vci_check 拿到的是不是使用者原檔（改名頂替後重跑工具），程式無法判定，
#      驗收看工具紀錄與使用者來源（S7，稽核 r8）；miko_refs 只核「路徑@commit」格式，不核 commit 是否存在。
# 結束碼：0＝PASS；1＝FAIL（逐條列出）；2＝用法錯誤或檔案讀不到；4＝NOT_RUN（probe 沒跑）或 NOT_READ（抽格失敗），S7 都不算 PASS
import csv, datetime, hashlib, json, math, re, sys, unicodedata

KINDS = {'observed', 'author_claim', 'user_provided', 'inference'}
STATUS = {'VERIFIED', 'CONTRADICTED', 'UNVERIFIED', 'INFERENCE', 'UNKNOWN', 'NOT_READ'}
MODES = {'content_only', 'content_and_miko'}
MEDIA_KINDS = {'image', 'video', 'audio', 'url_only'}
REF = re.compile(r'[^@\s]+@[0-9a-f]{7,40}')
PID = re.compile(r'(?<![A-Za-z0-9_])(P\d+)\b')   # 稽核 r5 N3：任何位置的 P＋數字都算提案編號
DATE_LINE = re.compile(r'發布：(\d{4}-\d{2}-\d{2}|UNKNOWN)｜生效：(\d{4}-\d{2}-\d{2}|UNKNOWN)｜查閱：\d{4}-\d{2}-\d{2}')


ZW = dict.fromkeys(map(ord, '\ufeff\u200b\u200c\u200d\u2060'))   # BOM 與零寬字元


def _norm_id(x):   # 稽核 r9：id 先 NFKC、去零寬與空白再比
    return unicodedata.normalize('NFKC', x).translate(ZW).strip() if isinstance(x, str) else x


def _ev_ok(ev):   # evidence 合格：非空 list，每項是物件，有 http(s) url 與整行日期一行（稽核 r10：T-V11 路徑共用）
    return isinstance(ev, list) and bool(ev) and all(isinstance(e, dict) and re.match(r'https?://\S+$', str(e.get('url', ''))) and _date_line(e.get('dates')) for e in ev)


def _is_json(t):
    try: json.loads((t or '').lstrip('\ufeff')); return True
    except ValueError: return False


def _not_future(d):   # 查閱日不得晚於執行當天（容許 +1 天時差）
    return datetime.date.fromisoformat(d) <= datetime.date.today() + datetime.timedelta(days=1)


def _date_line(v):
    mm = DATE_LINE.fullmatch(str(v or '').strip())
    if not mm: return False
    try:
        for d in re.findall(r'\d{4}-\d{2}-\d{2}', mm.group(0)): datetime.date.fromisoformat(d)
        return _not_future(re.search(r'查閱：(\d{4}-\d{2}-\d{2})', mm.group(0)).group(1))
    except ValueError: return False


def _proposal_heads(txt):
    # 二級標題照 Markdown 判：ATX（0～3 空白＋## 後接空白、tab 或行尾）與 setext（非空行＋下一行全是 -）；回傳（P 編號清單, 不合格標題）
    # 稽核 r9：圍欄依字元種類與長度配對；H1（ATX「# 」或 setext「===」）只准出現在第一個標題
    lines, ids, bad, fence, seen_head = txt.splitlines(), [], [], None, False
    for i, l in enumerate(lines):
        fm = re.match(r' {0,3}(`{3,}(?!.*`)|~{3,})', l)
        if fence:
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= len(fence) and not l.strip().strip(fence[0]): fence = None
            continue
        if fm: fence = fm.group(1); continue
        h1 = re.match(r' {0,3}#(?:[ \t]|$)', l) or (re.match(r' {0,3}=+[ \t]*$', l) and i and lines[i - 1].strip())
        if h1:
            if seen_head: bad.append(l.strip() + '（H1 只能是第一個標題）')
            seen_head = True; continue
        h = None
        mm = re.match(r' {0,3}##(?:[ \t]+(.*?))?[ \t#]*$', l)
        if mm: h = (mm.group(1) or '').strip()
        elif re.match(r' {0,3}-+[ \t]*$', l) and i and lines[i - 1].strip() and not re.match(r' {0,3}([#>*+-]|\d+[.)])', lines[i - 1]):
            h = lines[i - 1].strip()
        if h is None: continue
        seen_head = True
        pm = re.match(r'(P\d+)\b', h)
        if pm: ids.append(pm.group(1))
        else: bad.append(l.strip() if mm else h + '（setext）')
    dup = sorted({x for x in ids if ids.count(x) > 1})
    return bad + [f'{x} 重複（同一編號只能一個標題）' for x in dup]


def check(a, frames_idx=None, frames_t=None, proposal_ids=None, frames_src=None, probe=None, subs_sha=None, proposal_heads=None):
    err, info = [], []
    if a.get('request_mode') not in MODES: err.append(f'K6 request_mode 缺或不合法：{a.get("request_mode")}（只能 content_only／content_and_miko）')
    s = a.get('source', {})
    if not (s.get('url') or s.get('file')): err.append('K1 source 沒有 url 也沒有 file')
    if s.get('url') and not re.match(r'https?://\S+$', str(s.get('url'))): err.append('K1 source.url 要是 http(s) 網址')
    if s.get('file') and not re.fullmatch(r'[0-9a-f]{64}', str(s.get('sha256', ''))): err.append('K1 有 file 但 sha256 缺或格式不對')
    try:
        ok_date = bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(s.get('retrieved', '')))) and _not_future(s['retrieved'])
    except ValueError: ok_date = False
    if not ok_date: err.append('K1 缺查閱日期 retrieved（YYYY-MM-DD，要是真的日期）')
    if (a.get('media') or {}).get('kind') in ('image', 'video') and 'complete' not in a: err.append('K0 image／video 一定要寫 complete（true／false）')
    if 'complete' in a and not isinstance(a.get('complete'), bool): err.append(f'K0 complete 只能是 true 或 false（現在是 {a.get("complete")!r}）')
    m = a.get('media', {})
    viewed = set(m.get('frames_viewed', []))
    mk = m.get('kind')
    fr_nr = mk == 'video' and m.get('frames_status') == 'NOT_READ'   # 稽核 r15：抽格失敗（vci_media frames 結束碼 1／3）的出口
    if fr_nr:
        if frames_idx is not None: err.append('K2 media.frames_status＝NOT_READ 卻帶了 --frames（互相矛盾）')
        if not str(m.get('frames_reason') or '').translate(ZW).strip(): err.append('K2 frames_status＝NOT_READ 要在 media.frames_reason 寫抽格失敗的結束碼與原因')
        if a.get('complete') is True: err.append('K2 抽格失敗（frames_status＝NOT_READ）時 complete 不得為 true')
        info.append(f'K2 抽格 NOT_READ（{m.get("frames_reason")}）：影片內容只依直接看到的第一張，本次最多 NOT_READ')
    if mk not in MEDIA_KINDS: err.append(f'K2 media.kind 缺或不合法：{mk}（只能 image／video／audio／url_only）')
    if s.get('file'):
        if probe is None: err.append('K2 來源是檔案，要帶 --probe（vci_media.py probe 的 JSON），種類以程式探測為準')
        else:
            if probe.get('sha256') != s.get('sha256'): err.append('K2 probe 的 sha256 和 source.sha256 不同（探測的不是這個檔）')
            if probe.get('file') != str(s.get('file')).replace('\\', '/').rsplit('/', 1)[-1]:
                err.append(f'K2 probe 的 file（{probe.get("file")}）和 source.file 的檔名不同（探測的不是這個檔）')
            if probe.get('status') == 'NOT_RUN':
                info.append('K2 probe NOT_RUN（本機沒有 ffprobe）：種類與串流未經程式探測，本次最多 NOT_RUN')
            else:
                if probe.get('kind') != mk: err.append(f'K2 media.kind（{mk}）和 probe 判定（{probe.get("kind")}）不同')
                ps = probe.get('streams')
                if not isinstance(ps, dict): err.append('K2 probe JSON 不完整（沒有 streams），要用 vci_media.py probe 重跑')
                elif m.get('streams') != ps: err.append(f'K3 media.streams（{m.get("streams")}）和 probe.streams（{ps}）不同，串流以 probe 為準')
                vd = probe.get('video_duration_s')   # 稽核 r13：密度以影像串流長度為準，沒有才退回容器長度
                dur = vd if isinstance(vd, (int, float)) and vd > 0 else probe.get('duration_s')
                if mk == 'video' and not fr_nr and not isinstance(dur, (int, float)):
                    if str(m.get('sparse_reason') or '').translate(ZW).strip(): info.append(f'K2 影片長度不明，抽格密度未核（理由：{m.get("sparse_reason")}）')
                    else: err.append('K2 影片 probe 沒有長度（duration_s 不是數字），無法核抽格密度；要在 media.sparse_reason 寫理由')
                if mk == 'video' and isinstance(dur, (int, float)) and frames_idx is not None:
                    want = 2 if dur < 60 else 10
                    ts = sorted(frames_t.values()) if frames_t else []
                    # 稽核 r14：兩張以上時直接核抽格間隔（frames.csv 的 t_sec 差＝--every），不再用「長度÷間隔」推張數，
                    #   容器長度比影像長（FLV、WMV 音軌較長）也不會誤擋；只有一張時才用張數（max(1, 長度÷間隔四捨五入)，稽核 r12）
                    if len(ts) >= 2: short, msg = (ts[1] - ts[0]) > want + 1e-6, f'K2 影片 {dur} 秒每 {round(ts[1] - ts[0], 3)} 秒抽一張，比預設密度（每 {want} 秒）疏'
                    else:
                        need = max(1, math.floor(dur / want + 0.5))
                        short, msg = len(frames_idx) < need, f'K2 影片 {dur} 秒只抽 {len(frames_idx)} 張，少於預設密度需要的 {need} 張'
                    if short:
                        if str(m.get('sparse_reason') or '').translate(ZW).strip():
                            info.append(msg + f'（理由：{m.get("sparse_reason")}）')
                            if a.get('complete') is True: err.append('K2 抽格少於預設密度（寫了 sparse_reason）時 complete 不得為 true')
                        else: err.append(msg + '；要較疏請在 media.sparse_reason 寫理由')
    elif mk in ('image', 'video', 'audio'):
        err.append(f'K2 沒有 source.file 卻寫 media.kind＝{mk}；只有網址時寫 url_only')
    if mk == 'url_only':
        if a.get('complete') is True: err.append('K2 url_only（只有網址）時 complete 不得為 true')
        if m.get('audio_status') != 'NOT_READ': err.append('K3 url_only（只有網址，沒讀到媒體）時 audio_status 只能 NOT_READ')
        if any(isinstance(c, dict) and c.get('kind') == 'observed' for c in a.get('claims', [])):
            err.append('K4 url_only（只有網址，沒看到媒體）時不得有 observed 主張')
    if mk == 'audio' and m.get('audio_status') == 'NOT_READ' and a.get('complete') is True:
        err.append('K2 音訊檔 audio_status＝NOT_READ（內容沒讀到）時 complete 不得為 true')
    if m.get('kind') == 'video' and frames_idx is None and not fr_nr:
        err.append('K2 影片沒有附 frames.csv（--frames），無法核對看了哪些影格')
    if frames_src is not None:
        if any(x is None or x == '' for x in frames_src): err.append('K2 frames.csv 缺 source_sha256 欄（要用 vci_media.py frames 重抽）')
        elif any(x != s.get('sha256') for x in frames_src): err.append('K2 frames.csv 的 source_sha256 和 source.sha256 不同（影格不是從這支影片抽的）')
        if m.get('frames_total') != len(frames_src): err.append(f'K2 media.frames_total（{m.get("frames_total")}）和 frames.csv 列數（{len(frames_src)}）不同')
    if frames_idx is not None:
        extra = sorted(viewed - frames_idx)
        if extra: err.append(f'K2 frames_viewed 有 frames.csv 裡沒有的影格：{extra}')
        cov = len(viewed & frames_idx)
        info.append(f'K2 影格覆蓋 {cov}/{len(frames_idx)}')
        if cov < len(frames_idx) and a.get('complete') is True: err.append(f'K2 只看了 {cov}/{len(frames_idx)} 張影格，complete 不得為 true')
    st = probe.get('streams') if isinstance(probe, dict) and isinstance(probe.get('streams'), dict) else m.get('streams', {})
    tr, tr_ok = a.get('transcript'), False
    if tr not in (None, '', {}):
        if not isinstance(tr, dict) or tr.get('type') not in ('subs', 'user_file') or not tr.get('file') or \
                not re.fullmatch(r'[0-9a-f]{64}', str(tr.get('sha256', ''))):
            err.append('K3 transcript 要寫成 {"type": "subs"|"user_file", "file": …, "sha256": 64 位 hex}（字串或缺欄位不算逐字稿來源）')
        elif tr['type'] == 'subs' and isinstance(probe, dict) and probe.get('status') != 'NOT_RUN' and not st.get('subtitle', 0):
            err.append('K3 transcript 寫 subs，但 probe 顯示沒有字幕軌（字幕要用 vci_media.py subs 抽）')
        elif subs_sha is None:
            err.append('K3 寫了 transcript 但沒帶 --transcript <檔>，無法核對逐字稿 SHA-256（手填 hex 不算）')
        elif subs_sha['sha256'] != tr['sha256']:
            err.append('K3 --transcript 給的檔案 SHA-256 和 transcript.sha256 不同')
        elif tr['sha256'] == s.get('sha256'):
            err.append('K3 transcript 指向來源媒體本身（sha256＝source.sha256），不是逐字稿')
        elif subs_sha['name'] != str(tr['file']).replace('\\', '/').rsplit('/', 1)[-1]:
            err.append(f'K3 --transcript 的檔名（{subs_sha["name"]}）和 transcript.file 不同')
        elif subs_sha['sha256'] in subs_sha.get('inputs', ()):
            err.append('K3 --transcript 和同一次呼叫的 analysis.json／probe／frames／PROPOSAL.md 是同一個檔，不是逐字稿')
        elif not subs_sha['bytes'] or (subs_sha['text'] is not None and not any(ch.isalnum() for ch in subs_sha['text'].translate(ZW))):
            err.append('K3 --transcript 是空檔或只有空白／BOM／零寬字元，不算逐字稿')
        elif subs_sha['name'] in ('ANALYSIS.md', 'PROPOSAL.md', 'analysis.json', 'probe.json', 'frames.csv') or \
                re.match(r'(INFO K\d|FAIL K\d|PASS$|NOT_RUN)', (subs_sha['text'] or '').lstrip('\ufeff').lstrip(), re.M):
            err.append('K3 --transcript 是本 Skill 自己產生的檔或 vci_check 的輸出，不是逐字稿')
        elif _is_json(subs_sha['text']) or (subs_sha['text'] or '').lstrip().startswith('idx,t_sec'):
            err.append('K3 --transcript 是 JSON 或 frames.csv 格式（像 analysis.json／probe.json），不是逐字稿')
        elif subs_sha['text'] is None: err.append('K3 --transcript 不能用 UTF-8 解碼，不是文字逐字稿')
        elif tr['type'] == 'subs' and '-->' not in subs_sha['text']: err.append('K3 transcript 寫 subs，但檔案沒有字幕時間碼「-->」')
        else: tr_ok = True
    if st.get('audio', 0) > 0 and not tr_ok and m.get('audio_status') != 'NOT_READ':
        err.append('K3 有音軌但沒有逐字稿來源，audio_status 必須是 NOT_READ')
    ids = set()
    for c in a.get('claims', []):
        cid = c.get('id')
        if not isinstance(cid, str) or not cid.strip(): err.append(f'K4 主張 id 要是非空字串（現在是 {cid!r}）')
        if _norm_id(cid) in {_norm_id(x) for x in ids}: err.append(f'K4 主張 id 重複（NFKC、去空白與零寬後相同）：{cid!r}')
        ids.add(cid)
        if c.get('kind') not in KINDS: err.append(f'K4 {cid} kind 不合法：{c.get("kind")}')
        if c.get('status') not in STATUS: err.append(f'K4 {cid} status 不合法：{c.get("status")}')
        if c.get('kind') == 'observed':
            loc = c.get('locator', {})
            if 'frame' not in loc and 't_sec' not in loc and 'region' not in loc: err.append(f'K4 {cid} 畫面主張沒有 locator')
            if mk in ('video', 'audio') and not fr_nr and 'frame' not in loc and 't_sec' not in loc:
                err.append(f'K4 {cid} 影片的畫面主張要有 frame 或 t_sec（只寫 region 看不出是哪一張）')
        loc = c.get('locator', {})   # 稽核 r5 N2：所有 kind 帶 frame／t_sec 都核對
        if not isinstance(loc, dict): raise TypeError(f'{cid} locator 不是物件')
        if ('frame' in loc or 't_sec' in loc) and frames_t is None:
            err.append(f'K4 {cid} 寫了 frame／t_sec 但沒帶 --frames，無法核對')
        if 'frame' in loc and loc['frame'] not in viewed:
            err.append(f'K4 {cid} 引用的影格 {loc["frame"]} 不在 frames_viewed（沒看過的畫面不得描述）')
        if 't_sec' in loc and frames_t is not None:
            seen_t = {frames_t[i] for i in viewed if i in frames_t}
            if 'frame' in loc: seen_t = {frames_t[loc['frame']]} if loc['frame'] in viewed and loc['frame'] in frames_t else set()
            if not any(abs(float(loc['t_sec']) - t) < 1e-6 for t in seen_t):
                err.append(f'K4 {cid} 的 t_sec {loc["t_sec"]} 不是已看影格（或所寫 frame）的時間（沒看過的畫面不得描述）')
        # 稽核 r11：只在有音軌的影片／音訊套用（圖卡、只有網址的作者主張用 region 或貼文原句，不會是口述）
        if c.get('kind') == 'author_claim' and mk in ('video', 'audio') and st.get('audio', 0) > 0 and not tr_ok and 'frame' not in loc and 't_sec' not in loc and not _ev_ok(c.get('evidence')):
            err.append(f'K4 {cid} 作者主張沒有逐字稿、沒有畫面定位（frame／t_sec），也沒有合格的來源 evidence（http(s) url＋日期一行），講者說的話不得憑推測寫（T-V11）')
        if c.get('kind') == 'inference' and c.get('status') not in ('INFERENCE', 'UNKNOWN'):
            err.append(f'K4 {cid} 是推論，status 只能 INFERENCE 或 UNKNOWN')
        if c.get('kind') == 'observed' and c.get('status') not in ('VERIFIED', 'UNKNOWN'):
            err.append(f'K4 {cid} 是畫面主張，status 只能 VERIFIED（看清楚）或 UNKNOWN（看不清）')
        if c.get('status') in ('VERIFIED', 'CONTRADICTED') and c.get('kind') != 'observed':
            if not _ev_ok(c.get('evidence')):
                err.append(f'K4 {cid} 標 {c.get("status")} 但 evidence 缺 url 或日期一行')
    used = set()
    items = a.get('proposal_items', [])
    for p in items:
        pid, cl = p.get('id'), p.get('claim_ids', [])
        if not cl: err.append(f'K5 OUTPUT_ONLY：{pid} 沒有引用任何主張')
        miss = [x for x in cl if x not in ids]
        if miss: err.append(f'K5 OUTPUT_ONLY：{pid} 引用不存在的主張 {miss}')
        refs = p.get('miko_refs')
        if not refs: err.append(f'K5 {pid} 沒有 miko_refs（沒讀 MIKO 檔就提建議）')
        elif not isinstance(refs, list) or not all(isinstance(r, str) and REF.fullmatch(r) for r in refs):
            err.append(f'K5 {pid} miko_refs 要寫成 路徑@commit（7～40 位 hex），才看得出讀的是哪一版')
        used |= set(cl)
    if items:
        unused = sorted(ids - used, key=str)
        if unused: info.append(f'K5 SOURCE_ONLY（只提示）：沒有被任何建議引用的主張 {unused}')
    if a.get('request_mode') == 'content_only' and items:
        err.append('K6 使用者只問內容（content_only），不得產出 proposal_items')
    if proposal_ids is None and (items or a.get('request_mode') == 'content_and_miko'):
        err.append('K7 有 proposal_items 或 request_mode＝content_and_miko，一定要帶 --proposal <PROPOSAL.md> 對帳')
    if proposal_ids is not None:
        for h in proposal_heads or []: err.append(f'K7 PROPOSAL.md 的二級標題要寫成「## P數字 …」、編號不重複：{h}')
        jids = {p.get('id') for p in items}
        more, less = sorted(proposal_ids - jids), sorted(jids - proposal_ids, key=str)
        if more: err.append(f'K7 OUTPUT_ONLY：PROPOSAL.md 有 {more}，analysis.json 的 proposal_items 沒有（沒有來源主張）')
        if less: err.append(f'K7 PROPOSAL.md 漏寫 {less}')
    return err, info


def main(argv):
    if not argv:
        print('用法：vci_check.py <analysis.json> [--probe <probe.json>] [--frames <frames.csv>] [--proposal <PROPOSAL.md>] [--transcript <字幕或逐字稿檔>]'); return 2
    try:
        a = json.load(open(argv[0], encoding='utf-8'))
    except (OSError, ValueError) as ex:
        print(f'NOT_READ：{ex}'); return 2
    fi = ft = pi = fs = pr = ss = None
    ph = None
    topt = '--transcript' if '--transcript' in argv else '--subs' if '--subs' in argv else None
    if topt:
        try:
            tpath = argv[argv.index(topt) + 1]; tb = open(tpath, 'rb').read()
            try: ttxt = tb.decode('utf-8')
            except UnicodeDecodeError: ttxt = None
            ss = {'sha256': hashlib.sha256(tb).hexdigest(), 'name': tpath.replace('\\', '/').rsplit('/', 1)[-1], 'bytes': len(tb), 'text': ttxt}
        except (OSError, IndexError) as ex:
            print(f'NOT_READ 字幕檔：{ex}'); return 2
    if '--probe' in argv:
        try:
            pr = json.load(open(argv[argv.index('--probe') + 1], encoding='utf-8'))
        except (OSError, IndexError, ValueError) as ex:
            print(f'NOT_READ probe.json：{ex}'); return 2
    if '--frames' in argv:
        try:
            with open(argv[argv.index('--frames') + 1], encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            ft = {int(r['idx']): float(r['t_sec']) for r in rows}; fi = set(ft)
            fs = [r.get('source_sha256') for r in rows]
        except (OSError, IndexError, KeyError, ValueError) as ex:
            print(f'NOT_READ frames.csv：{ex}'); return 2
    if '--proposal' in argv:
        try:
            txt = unicodedata.normalize('NFKC', open(argv[argv.index('--proposal') + 1], encoding='utf-8-sig').read())
            pi = set(PID.findall(txt)); ph = _proposal_heads(txt)
        except (OSError, IndexError) as ex:
            print(f'NOT_READ PROPOSAL.md：{ex}'); return 2
    if not isinstance(a, dict):
        print('FAIL K0 analysis.json 最外層要是物件'); print('FAIL 共 1 項'); return 1
    try:
        if isinstance(ss, dict):
            ins = set()
            for i, x in enumerate(argv):
                if i == 0 or (i > 0 and argv[i - 1] in ('--probe', '--frames', '--proposal')):
                    try: ins.add(hashlib.sha256(open(x, 'rb').read()).hexdigest())
                    except OSError: pass
            ss['inputs'] = ins
        err, info = check(a, fi, ft, pi, fs, pr if isinstance(pr, dict) else ({} if pr is not None else None), ss, ph)
    except (AttributeError, TypeError, ValueError) as ex:   # 欄位型別不對：照 FAIL 處理，不丟 traceback
        print(f'FAIL K0 欄位結構不對：{type(ex).__name__}：{ex}'); print('FAIL 共 1 項'); return 1
    for x in info: print('INFO', x)
    for x in err: print('FAIL', x)
    if err:
        print(f'FAIL 共 {len(err)} 項'); return 1
    m0 = a.get('media') if isinstance(a.get('media'), dict) else {}
    if m0.get('kind') == 'video' and m0.get('frames_status') == 'NOT_READ':
        print('NOT_READ（抽格失敗：影片內容只依直接看到的畫面；其他項無 FAIL，但 S7 不算 PASS）'); return 4
    if isinstance(pr, dict) and pr.get('status') == 'NOT_RUN':
        print('NOT_RUN（沒有 ffprobe：種類與串流未經程式探測；其他項無 FAIL，但 S7 不算 PASS）'); return 4
    print('PASS'); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
