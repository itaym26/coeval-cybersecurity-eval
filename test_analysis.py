"""Synthetic-fixture checks only, not validation of the historical results.
Run from the repository root: python3 test_analysis.py
"""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as td:
    run = Path(td)
    for script in sorted(ROOT.glob('runs/*/*.py')):
        result = subprocess.run([sys.executable, str(script), str(run)], capture_output=True, text=True)
        assert result.returncode != 0 and 'No raw evaluation JSONL files' in result.stderr, (script, result)
    print('PASS: all five analysis scripts reject missing raw data clearly')
    ev = run / 'phase5_evaluations'
    ev.mkdir()
    records = [
        {'response_id':'topic__teacher__q__studentA', 'judge_model_id':'judge1','scores':{'one':'High','two':'Medium'}},
        {'response_id':'topic__teacher__q__studentB', 'judge_model_id':'judge1','scores':{'one':'Low','two':'Medium'}},
    ]
    (ev/'fixture.jsonl').write_text('\n'.join(map(json.dumps,records))+'\nnot-json\n',encoding='utf-8')
    for script in sorted(ROOT.glob('runs/*/compute_ranking.py')):
        result = subprocess.run([sys.executable,str(script),str(run)],capture_output=True,text=True,check=True)
        assert 'studentA' in result.stdout and '0.750' in result.stdout, result.stdout
        assert 'studentB' in result.stdout and '0.250' in result.stdout, result.stdout
        assert 'records 3 valid 2' in result.stdout, result.stdout
        print('PASS:',script.parent.name,'fixture ranking and malformed-line skip')
print('Synthetic fixtures passed. Historical measurements require the original exported JSONL files.')
