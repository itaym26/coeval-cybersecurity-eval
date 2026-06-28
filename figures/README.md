# Figures

Vector charts (SVG) used by the README, the landing page, and the per-run pages.

### Shared
| File | Description |
|------|-------------|
| `banner.svg` | Project banner (shield motif + Teacher/Student/Judge roles) |

### Run A
| File | Description |
|------|-------------|
| `runA_ranking.svg` | Run A — 2-model ranking (partial cloud run) |

### Run B
| File | Description |
|------|-------------|
| `runB_ranking.svg` | Run B — 4-model ranking |

### Run C
| File | Description |
|------|-------------|
| `runC_ranking.svg` | Run C — 7-model ranking |
| `judge_strictness.svg` | Run C — mean score awarded per judge (bias) |
| `size_vs_score.svg` | Run C — model size vs. score scatter (non-monotonic) |

All charts are generated from the run data; the underlying numbers are reproducible via the
`compute_ranking.py` / `analyze_stats.py` scripts in each run's folder under [`../runs/`](../runs/).
The full interactive CoEval reports (rendered, with live Plotly charts) are linked from the README and
the [landing page](https://itaym26.github.io/coeval-cybersecurity-eval/).
