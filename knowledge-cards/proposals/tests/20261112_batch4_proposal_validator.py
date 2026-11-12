#!/usr/bin/env python3
"""批次 4 提案層驗證器：只讀檔案，不連網、不修改正式路徑。"""
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[3]
PROPOSALS = ROOT / 'knowledge-cards' / 'proposals' / 'skills' / '20261112_batch4'
EXPECTED = ['dghp-travel','gmail-cleanup','grilling','label-foreign-text','make-skill','multi-agent-coordination-engine','photo-inspection-log','tw-alert-check','tw-backtest-workflow','visual-content-intelligence']
REQUIRED_MARKERS = ['PROPOSED', 'NOT_ADOPTED', 'HISTORICAL_NOT_RUNTIME']
FORBIDDEN_ADOPTION = ['ADOPTED', 'EFFECTIVE', 'Runtime 生效', '已採用']


def fail(message):
    print('FAIL', message)
    raise SystemExit(1)


def main():
    if not PROPOSALS.is_dir():
        fail(f'提案目錄不存在: {PROPOSALS}')
    found = []
    for name in EXPECTED:
        path = next(PROPOSALS.glob(f'*-{name}/SKILL.md'), None)
        if path is None:
            fail(f'缺少 {name}/SKILL.md')
        text = path.read_text(encoding='utf-8')
        if not text.startswith('未驗收提案'):
            fail(f'{path} 第一行不是未驗收提案')
        for marker in REQUIRED_MARKERS:
            if marker not in text:
                fail(f'{path} 缺少 {marker}')
        # 正式採用字樣只能出現在否定／門檻語境；不接受裸採用狀態。
        if 'adoption_status: ADOPTED' in text or 'status: EFFECTIVE' in text:
            fail(f'{path} 出現正式採用狀態')
        found.append((path, hashlib.sha256(text.encode()).hexdigest(), len(text)))
    outside = []
    for p in ROOT.glob('skills/20261112_batch4/*'):
        outside.append(str(p))
    if outside:
        fail(f'意外掃到正式路徑: {outside}')
    print(f'PASS proposal_count={len(found)}')
    for path, digest, size in found:
        print(f'PASS {path.relative_to(ROOT)} bytes={size} sha256={digest}')
    print('PASS proposal_status=PROPOSED_NOT_ADOPTED')
    print('PASS route_boundary=knowledge-cards/proposals-only')
    print('NOT_RUN Gemini consensus / independent audit / Runtime integration / CI')
    return 0


if __name__ == '__main__':
    sys.exit(main())
