import json, glob, os
from collections import defaultdict

RUN = r"C:\Users\itaym\CoEval\Runs\cybersecurity-run-C-large"
VAL = {'high': 1.0, 'medium': 0.5, 'low': 0.0}

# datapoints: id -> {prompt, attrs, teacher, reference}
dp = {}
for f in glob.glob(os.path.join(RUN, "phase3_datapoints", "*.jsonl")):
    for line in open(f, encoding='utf-8'):
        try: d = json.loads(line)
        except: continue
        dp[d['id']] = d

# responses: response_id -> {text, student, datapoint_id}
resp = {}
for f in glob.glob(os.path.join(RUN, "phase4_responses", "*.jsonl")):
    for line in open(f, encoding='utf-8'):
        try: d = json.loads(line)
        except: continue
        rid = d.get('id')
        if rid:
            resp[rid] = d

# evals: response_id -> judge -> scores
ev = defaultdict(dict)
for f in glob.glob(os.path.join(RUN, "phase5_evaluations", "*.jsonl")):
    for line in open(f, encoding='utf-8'):
        try: d = json.loads(line)
        except: continue
        rid = d.get('response_id'); j = d.get('judge_model_id')
        if rid and j: ev[rid][j] = d.get('scores', {})

def mean_score(sc):
    vs=[VAL[str(v).lower()] for v in sc.values() if str(v).lower() in VAL]
    return sum(vs)/len(vs) if vs else None

# Pick 3 example responses: one high-consensus, one low, one high-disagreement
scored = []
for rid, jd in ev.items():
    ms = [mean_score(s) for s in jd.values()]
    ms = [m for m in ms if m is not None]
    if len(ms) >= 5:
        avg = sum(ms)/len(ms)
        spread = max(ms)-min(ms)
        scored.append((rid, avg, spread))

best = max(scored, key=lambda x: x[1])
worst = min(scored, key=lambda x: x[1])
disagree = max(scored, key=lambda x: x[2])

for label, (rid, avg, spread) in [("HIGH-SCORING", best), ("LOW-SCORING", worst), ("HIGH-DISAGREEMENT", disagree)]:
    r = resp.get(rid, {})
    d = dp.get(r.get('datapoint_id',''), {})
    parts = rid.split('__')
    student = parts[3] if len(parts)>=4 else '?'
    print("="*70)
    print(f"[{label}]  student={student}  mean={avg:.2f}  spread={spread:.2f}")
    print("="*70)
    print("ATTRS:", d.get('sampled_target_attributes', {}))
    print("\nQUESTION (teacher=%s):" % d.get('teacher_model_id','?'))
    print(" ", (d.get('prompt','') or '')[:500])
    print("\nANSWER (student=%s):" % student)
    print(" ", (r.get('response','') or '')[:600])
    print("\nJUDGE SCORES (mean per judge):")
    for j in sorted(ev[rid]):
        print(f"   {j:14s} {mean_score(ev[rid][j]):.2f}   {ev[rid][j]}")
    print()
