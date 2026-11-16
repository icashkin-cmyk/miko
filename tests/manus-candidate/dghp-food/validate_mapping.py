from pathlib import Path
import json,hashlib
base=Path(__file__).parent
root=base.parent.parent.parent
src=Path('/home/ubuntu/work/github-miko-target/skills/dghp-food/SKILL.md')
cand=root/'skills/dghp-food/SKILL.md'
data=json.loads((base/'source-atom-map.json').read_text(encoding='utf-8'))
assert hashlib.sha256(src.read_bytes()).hexdigest()==data['source_sha256']
assert hashlib.sha256(cand.read_bytes()).hexdigest()==data['candidate_sha256']
assert len(data['atoms'])==54
assert all(a['mapping_status']=='MAPPED' and a['candidate_anchor'] for a in data['atoms'])
text=cand.read_text(encoding='utf-8')
assert 'Candidate Reconstruction Status' in text
print('source_sha256=PASS')
print('candidate_sha256=PASS')
print('atom_count=54')
print('candidate_anchor_coverage=54/54')
print('orphan_source_atoms=0')
print('mapping_result=PASS')
