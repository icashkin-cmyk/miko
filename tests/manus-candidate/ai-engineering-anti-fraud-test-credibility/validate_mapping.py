from pathlib import Path
import json, hashlib
base=Path(__file__).parent
root=base.parent.parent.parent
source=Path('/home/ubuntu/upload/pasted_content.txt')
candidate=root/'skills/ai-engineering-anti-fraud-test-credibility/SKILL.md'
data=json.loads((base/'source-atom-map.json').read_text(encoding='utf-8'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==data['source_sha256']
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==data['candidate_sha256']
text=candidate.read_text(encoding='utf-8')
assert all(a['mapping_status']=='MAPPED' and a['candidate_anchor'] in text for a in data['atoms'])
print('attachment_sha256=PASS')
print('candidate_sha256=PASS')
print('atom_count='+str(len(data['atoms'])))
print('mapping_result=PASS')
