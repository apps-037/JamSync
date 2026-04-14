# JamSync: AI-Powered Musician Matching

**Authors:** Apurva Saini, Yuvraj Anupam Chauhan  
**Course:** Foundations of Artificial Intelligence, Northeastern University  
**Date:** April 13, 2026  
**Repository:** [github.com/apps-037/JamSync](https://github.com/apps-037/JamSync)

---

## Overview

JamSync uses constraint satisfaction (CSP), adversarial search, and A* algorithms to schedule musicians into optimal jam sessions. The system processes 100 musicians in <3 seconds, achieving 37-54% match rates with 71-91% quality scores depending on algorithm configuration.

---

## Quick Start

```bash
# Install dependencies
pip install flask flask-cors numpy matplotlib

# Run CLI demo
python3 demo.py

# Or run algorithm comparison
python3 backend/csp_solver.py

# Or start web interface
python3 backend/api.py  # Terminal 1
cd frontend && python3 -m http.server 8000  # Terminal 2
# Open http://localhost:8000
```

---

## Project Structure

```
jamsync/
├── data/
│   ├── musicians_dataset.json       # 100 musician profiles
│   └── generate_dataset.py          # Dataset generator
├── backend/
│   ├── csp_solver.py                # CSP with forward checking
│   ├── adversarial_quality.py       # Nash Equilibrium predictor
│   ├── astar_grouping.py            # A* with domain heuristics
│   └── api.py                       # Flask REST API
├── analysis/
│   ├── create_visualizations.py     # Generate charts
│   ├── algorithm_comparison.png
│   └── quality_tradeoff.png
├── tests/
│   └── test_csp.py                  # Unit tests
├── frontend/
│   └── index.html                   # Web UI
└── demo.py                          # CLI interface
```

---

## How It Works

### 1. Constraint Satisfaction (CSP)

**Hard Constraints:**
- Availability overlap (all musicians free at same time)
- Group size (3-6 musicians)
- Rhythm section (≥1 drummer or bassist)
- No double-booking

**Soft Constraints:**
- Skill compatibility: 40% weight
- Genre overlap: 40% weight
- Personality balance: 20% weight

**Algorithm:** Backtracking with forward checking, constraint ordering

### 2. Adversarial Search

Models musicians with competing objectives (spotlight time, skill validation, genre comfort). Uses Nash Equilibrium: session is stable if no musician would unilaterally leave (min utility > 60%).

**Quality Formula:**
```
Q = 0.4×mean(utility) + 0.4×min(utility) + 0.2×(100 - variance)
```

### 3. A* Search

Finds optimal groups using four heuristics:
- **Instrument synergy** (30%): Rewards balanced combinations
- **Skill variance** (30%): Goldilocks principle (1-3 point spread)
- **Genre consensus** (25%): Requires shared vocabulary
- **Role balance** (15%): 1-2 leaders optimal

---

## Results

| Algorithm | Sessions | Match Rate | Avg Quality | Runtime |
|-----------|----------|------------|-------------|---------|
| Greedy CSP | 10 | 54% | 71.1% | 0.8s |
| CSP + A* | 10 | 37% | 90.8% | 2.1s |
| Hybrid | 10 | 37% | 79.3% | 2.4s |

**Key Finding:** A* achieves 27.7% higher quality but matches fewer musicians, demonstrating fundamental quality-quantity tradeoff.

**Best Session:** A* found 100% quality session (bass, drums, guitar, keys with skills 3,6,6,6)

---

## Dataset

**Source:** Synthetically generated (100 musicians)  
**Distributions:** Guitar (30%), Vocals (20%), Keys (15%), Drums (10%), Bass (10%), Other (15%)  
**Skills:** Normal distribution (μ=6, σ=2), range [1-10]  
**Genres:** 10 categories, 2-4 per musician  
**Availability:** 2-6 slots from 42 possible windows  

**Regenerate:**
```bash
python3 data/generate_dataset.py
```

---

## Testing

```bash
python3 tests/test_csp.py
```

All tests validate:
- Constraint enforcement (group size, rhythm, availability)
- Quality scoring accuracy
- Solver correctness

---

## References

- Burke, E. K., et al. (1997). University timetabling using genetic algorithms and CSP
- Schaerf, A. (1999). Survey of automated timetabling. AI Review, 13(2), 87-127
- Gusfield, D. & Irving, R. W. (1989). The Stable Marriage Problem. MIT Press
