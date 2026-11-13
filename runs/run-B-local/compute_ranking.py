from pathlib import Path
import sys
"""Compute the CoEval student ranking and judge-bias breakdown for Run B.

Usage:
    py compute_ranking.py [path_to_run_folder]

Defaults to the sibling Run B evaluation folder. Maps the ordinal judge scores
High/Medium/Low -> 1.0/0.5/0.0 and averages across all judges and rubric factors.
"""
import json, glob, os, sys
from collections import defaultdict

run = str(Path(sys.argv[1]).resolve()) if len(sys.argv) > 1 else str(Path(__file__).resolve().parent)
evdir = os.path.join(run, "phase5_evaluations")
if not glob.glob(os.path.join(evdir, "*.jsonl")):
    raise SystemExit("No raw evaluation JSONL files found in " + evdir + ". Supply an exported run directory; committed reports alone cannot regenerate rankings.")
val = {'high': 1.0, 'medium': 0.5, 'low': 0.0}

agg = defaultdict(list)
byjudge = defaultdict(lambda: defaultdict(list))
nrec = 0; nvalid = 0
for f in glob.glob(os.path.join(evdir, "*.jsonl")):
    for line in open(f, encoding='utf-8'):
        nrec += 1
        try:
            d = json.loads(line)
        except Exception:
            continue
        parts = d.get('response_id', '').split('__')
        if len(parts) < 4:
            continue
        student = parts[3]
        judge = d.get('judge_model_id', '')
        vals = [val[str(v).lower()] for v in d.get('scores', {}).values() if str(v).lower() in val]
        if not vals:
            continue
        nvalid += 1
        m = sum(vals) / len(vals)
        agg[student].append(m)
        byjudge[judge][student].append(m)

print('records', nrec, 'valid', nvalid, '(%.0f%%)' % (100 * nvalid / max(nrec, 1)))
print()
print('=== STUDENT RANKING (mean normalized score, all judges) ===')
for s, v in sorted(agg.items(), key=lambda x: -sum(x[1]) / len(x[1])):
    print('  %-18s %.3f   (n=%d)' % (s, sum(v) / len(v), len(v)))
print()
print('=== BY JUDGE (rows = judge, shows each student score) ===')
for j in sorted(byjudge):
    print('  judge=%s:' % j)
    for s, v in sorted(byjudge[j].items(), key=lambda x: -sum(x[1]) / len(x[1])):
        print('      %-18s %.3f (n=%d)' % (s, sum(v) / len(v), len(v)))
