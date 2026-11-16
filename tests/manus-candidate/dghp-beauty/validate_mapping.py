from pathlib import Path
import json, hashlib
base=Path(__file__).parent
root=base.parent.parent.parent
source=Path('/home/ubuntu/work/github-miko-target/skills/dghp-beauty/SKILL.md')
candidate=root/'skills/dghp-beauty/SKILL.md'
data=json.loads((base/'source-atom-map.json').read_text(encoding='utf-8'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==data['source_sha256']
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==data['candidate_sha256']
text=candidate.read_text(encoding='utf-8')
ids=[a['source_atom_id'] for a in data['atoms']]
assert len(ids)==61 and len(ids)==len(set(ids))
missing=[a['candidate_anchor'] for a in data['atoms'] if a['candidate_anchor'] not in text]
assert not missing, missing
assert all(a['mapping_status']=='MAPPED' for a in data['atoms'])
assert 'GP-' not in text
print('source_sha256=PASS')
print('candidate_sha256=PASS')
print('source_atom_count=61')
print('candidate_anchor_coverage=61/61')
print('governance_gp_atoms_in_dghp_beauty=0')
print('mapping_result=PASS')
