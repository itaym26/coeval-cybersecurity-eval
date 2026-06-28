# Figures

Vector charts (SVG) used by the README, the landing page, and the documentation.

| File | Description | Used in |
|------|-------------|---------|
| `banner.svg` | Project banner (shield motif + Teacher/Student/Judge roles) | README, landing page |
| `runC_ranking.svg` | Run C — final 7-model ranking bar chart | README §5, landing page |
| `judge_strictness.svg` | Run C — mean score awarded per judge (bias) | README §5 |
| `size_vs_score.svg` | Model size vs. score scatter (non-monotonic) | README §5, landing page |

All charts are generated from the run data; the underlying numbers are reproducible via
`runs/run-C-local/compute_ranking.py` and `runs/run-C-local/analyze_stats.py`. The full interactive
CoEval reports (rendered, with live Plotly charts) are linked from the README and the
[landing page](https://itaym26.github.io/coeval-cybersecurity-eval/).
