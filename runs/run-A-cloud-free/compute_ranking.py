import json, glob, os
from collections import defaultdict

os.chdir(os.path.join(os.path.dirname(__file__), 'cybersecurity-run-05'))
val = {'high': 1.0, 'medium': 0.5, 'low': 0.0}
agg = defaultdict(list)
byjudge = defaultdict(lambda: defaultdict(list))
nrec = 0; nvalid = 0
for f in glob.glob('phase5_evaluations/*.jsonl'):
    for line in open(f, encoding='utf-8'):
        nrec += 1
        try:
            d = json.loads(line)
        except Exception:
            continue
        rid = d.get('response_id', '')
        parts = rid.split('__')
        if len(parts) < 4:
            continue
        student = parts[3]
        judge = d.get('judge_model_id', '')
        sc = d.get('scores', {})
        vals = [val[str(v).lower()] for v in sc.values() if str(v).lower() in val]
        if not vals:
            continue
        nvalid += 1
        m = sum(vals) / len(vals)
        agg[student].append(m)
        byjudge[judge][student].append(m)

print('records', nrec, 'valid', nvalid)
print()
print('=== STUDENT RANKING (mean normalized score, all judges) ===')
for s, v in sorted(agg.items(), key=lambda x: -sum(x[1]) / len(x[1])):
    print('  %-18s %.3f   (n=%d)' % (s, sum(v) / len(v), len(v)))
print()
print('=== BY JUDGE ===')
for j in sorted(byjudge):
    print('  judge=%s:' % j)
    for s, v in sorted(byjudge[j].items(), key=lambda x: -sum(x[1]) / len(x[1])):
        print('      %-18s %.3f (n=%d)' % (s, sum(v) / len(v), len(v)))
