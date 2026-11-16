from pathlib import Path
import json,hashlib
base=Path(__file__).parent
root=base.parent.parent.parent
src=Path('/home/ubuntu/work/github-miko-target/skills/dghp-travel/SKILL.md')
cand=root/'skills/dghp-travel/SKILL.md'
data=json.loads((base/'source-atom-map.json').read_text(encoding='utf-8'))
assert hashlib.sha256(src.read_bytes()).hexdigest()==data['source_sha256']
assert hashlib.sha256(cand.read_bytes()).hexdigest()==data['candidate_sha256']
assert len(data['atoms'])==50
assert all(a['mapping_status']=='MAPPED' and a['candidate_anchor'] for a in data['atoms'])
print('source_sha256=PASS')
print('candidate_sha256=PASS')
print('atom_count=50')
print('candidate_anchor_coverage=50/50')
print('orphan_source_atoms=0')
print('mapping_result=PASS')
