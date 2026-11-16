from pathlib import Path

ROOT = Path('/home/ubuntu/work/manus-miko-universal-governance-migration-v1')
SKILL = ROOT / 'skills/dghp-travel/SKILL.md'

def validate_route(text: str) -> None:
    required = [
        'version-evolution-preservation',
        '累積式升級與歷史版本保護路由',
        'archive/dghp-travel/<version>/',
        'SHA-256',
        '不得標記 `QUALIFIED_FOR_NEXT_STAGE`',
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise AssertionError('missing route controls: ' + ', '.join(missing))

original = SKILL.read_text(encoding='utf-8')
validate_route(original)
mutated = original.replace('version-evolution-preservation', 'REMOVED_ROUTE')
try:
    validate_route(mutated)
except AssertionError as exc:
    print('MUTATION_ROUTE_REMOVAL_REJECTED')
    print(str(exc))
else:
    raise AssertionError('mutation was not rejected')
print('ORIGINAL_ROUTE_ACCEPTED')
