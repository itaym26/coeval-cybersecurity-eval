r"""Quantitative statistics for the CoEval cybersecurity runs.

Computes, with no external dependencies:
  1. Inter-judge agreement  — pairwise Cohen's kappa over High/Medium/Low labels
  2. Self-preference index   — how much each model inflates its own score as judge
  3. Verbosity bias          — correlation of answer length with score,
                               single-judge vs ensemble (tests the paper's claim)
  4. Rank stability          — Spearman rho between Run B and Run C rankings

Usage:  py analyze_stats.py [run_dir]
Default run_dir = the Run C experiment folder.
"""
import json, glob, os, sys, math, itertools
from collections import defaultdict

RUN = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\itaym\CoEval\Runs\cybersecurity-run-C-large"
VAL = {'high': 1.0, 'medium': 0.5, 'low': 0.0}


def load_eval(run):
    """response_id -> judge -> {factor: label}; plus per (judge) records."""
    per = defaultdict(dict)
    for f in glob.glob(os.path.join(run, "phase5_evaluations", "*.jsonl")):
        for line in open(f, encoding='utf-8'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            rid = d.get('response_id', '')
            judge = d.get('judge_model_id', '')
            sc = d.get('scores', {})
            if rid and judge and sc:
                per[rid][judge] = sc
    return per


def load_responses(run):
    """response_id -> answer text (for verbosity)."""
    txt = {}
    # find the response text field name from the first record
    files = glob.glob(os.path.join(run, "phase4_responses", "*.jsonl"))
    field = None
    for f in files:
        for line in open(f, encoding='utf-8'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if field is None:
                for cand in ('response', 'response_text', 'output', 'answer', 'text', 'content'):
                    if cand in d and isinstance(d[cand], str):
                        field = cand
                        break
            rid = d.get('id') or d.get('response_id') or d.get('datapoint_id')
            if field and rid:
                txt[rid] = d.get(field, '')
    return txt, field


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float('nan')


def resp_mean_score(scoredict):
    vals = [VAL[str(v).lower()] for v in scoredict.values() if str(v).lower() in VAL]
    return mean(vals) if vals else None


def cohen_kappa(pairs):
    """pairs: list of (labelA, labelB) categorical. Returns kappa or None."""
    cats = sorted({c for ab in pairs for c in ab})
    n = len(pairs)
    if n == 0 or len(cats) < 2:
        return None
    idx = {c: i for i, c in enumerate(cats)}
    po = sum(1 for a, b in pairs if a == b) / n
    ma = [0] * len(cats)
    mb = [0] * len(cats)
    for a, b in pairs:
        ma[idx[a]] += 1
        mb[idx[b]] += 1
    pe = sum((ma[i] / n) * (mb[i] / n) for i in range(len(cats)))
    return (po - pe) / (1 - pe) if pe != 1 else None


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float('nan')
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else float('nan')


def spearman(xs, ys):
    def ranks(vs):
        order = sorted(range(len(vs)), key=lambda i: vs[i])
        r = [0.0] * len(vs)
        i = 0
        while i < len(vs):
            j = i
            while j + 1 < len(vs) and vs[order[j + 1]] == vs[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return pearson(ranks(xs), ranks(ys))


# ---------------------------------------------------------------- load
per = load_eval(RUN)
responses, field = load_responses(RUN)
judges = sorted({j for rid in per for j in per[rid]})
print(f"Run: {os.path.basename(RUN)}")
print(f"Responses scored: {len(per)} | Judges: {len(judges)} | response-text field: {field}\n")

# ---------------------------------------------------------------- 1. inter-judge kappa
print("=" * 64)
print("1. INTER-JUDGE AGREEMENT  (pairwise Cohen's kappa, High/Med/Low)")
print("=" * 64)
kappas = []
for ja, jb in itertools.combinations(judges, 2):
    pairs = []
    for rid, jd in per.items():
        if ja in jd and jb in jd:
            for factor in jd[ja]:
                if factor in jd[jb]:
                    la, lb = str(jd[ja][factor]).lower(), str(jd[jb][factor]).lower()
                    if la in VAL and lb in VAL:
                        pairs.append((la, lb))
    k = cohen_kappa(pairs)
    if k is not None:
        kappas.append((k, ja, jb))
kappas.sort(reverse=True)
for k, ja, jb in kappas:
    print(f"  kappa = {k:+.3f}   {ja} x {jb}")
if kappas:
    print(f"\n  range: {kappas[-1][0]:+.3f} .. {kappas[0][0]:+.3f}   (mean {mean(k for k,_,_ in kappas):+.3f})")

# ---------------------------------------------------------------- 2. self-preference
print("\n" + "=" * 64)
print("2. SELF-PREFERENCE INDEX  (self-as-judge score - others'-mean score)")
print("=" * 64)
# student -> judge -> [resp mean scores]
sj = defaultdict(lambda: defaultdict(list))
for rid, jd in per.items():
    parts = rid.split('__')
    if len(parts) < 4:
        continue
    student = parts[3]
    for judge, sc in jd.items():
        m = resp_mean_score(sc)
        if m is not None:
            sj[student][judge].append(m)
for student in sorted(sj):
    self_score = mean(sj[student].get(student, [])) if sj[student].get(student) else None
    others = [v for j, lst in sj[student].items() if j != student for v in lst]
    om = mean(others) if others else None
    if self_score is not None and om is not None:
        print(f"  {student:14s} self={self_score:.3f}  others={om:.3f}  bias={self_score-om:+.3f}")

# ---------------------------------------------------------------- 3. verbosity bias
print("\n" + "=" * 64)
print("3. VERBOSITY BIAS  (corr of answer length with score)")
print("=" * 64)
if field:
    # per response: length, ensemble mean score, and each judge's score
    lens, ens = [], []
    perjudge_xy = defaultdict(lambda: ([], []))
    for rid, jd in per.items():
        L = len(responses.get(rid, '') or '')
        if L == 0:
            continue
        jmeans = [resp_mean_score(sc) for sc in jd.values()]
        jmeans = [x for x in jmeans if x is not None]
        if not jmeans:
            continue
        lens.append(L); ens.append(mean(jmeans))
        for judge, sc in jd.items():
            m = resp_mean_score(sc)
            if m is not None:
                perjudge_xy[judge][0].append(L)
                perjudge_xy[judge][1].append(m)
    print(f"  ENSEMBLE  (mean of all judges):  Pearson r = {pearson(lens,ens):+.3f}   Spearman = {spearman(lens,ens):+.3f}   n={len(lens)}")
    print("  Single judges:")
    sj_corr = []
    for judge in sorted(perjudge_xy):
        xs, ys = perjudge_xy[judge]
        r = pearson(xs, ys)
        sj_corr.append(abs(r))
        print(f"    {judge:14s} Pearson r = {r:+.3f}   (n={len(xs)})")
    print(f"\n  mean |single-judge r| = {mean(sj_corr):.3f}   vs   |ensemble r| = {abs(pearson(lens,ens)):.3f}")
else:
    print("  (response-text field not found; skipping)")

# ---------------------------------------------------------------- 4. rank stability B vs C
print("\n" + "=" * 64)
print("4. RANK STABILITY  (Spearman rho, Run B vs Run C, common models)")
print("=" * 64)
runB = {'phi3': 0.898, 'llama3-8b': 0.860, 'qwen2.5-3b': 0.856, 'gemma2-2b': 0.798}
# recompute Run C student means here for the common models
cmean = defaultdict(list)
for rid, jd in per.items():
    parts = rid.split('__')
    if len(parts) < 4:
        continue
    student = parts[3]
    for sc in jd.values():
        m = resp_mean_score(sc)
        if m is not None:
            cmean[student].append(m)
runC = {s: mean(v) for s, v in cmean.items()}
common = [m for m in runB if m in runC]
xs = [runB[m] for m in common]
ys = [runC[m] for m in common]
print(f"  common models ({len(common)}): {', '.join(common)}")
for m in common:
    print(f"    {m:14s} B={runB[m]:.3f}  C={runC[m]:.3f}")
print(f"\n  Spearman rho (B vs C) = {spearman(xs, ys):+.3f}")
