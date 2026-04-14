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

# Run algorithm comparison (recommended)
python3 backend/csp_solver.py

# Or generate visualizations
python3 analysis/create_visualizations.py

# Or start web API
python3 backend/api.py
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
│   ├── create_visualizations.py     # Generate comparison charts
│   ├── algorithm_comparison.png     # 4-panel comparison
│   └── quality_tradeoff.png         # Scatter plot
├── frontend/
│   └── index.html                   # Web interface
├── tests/
│   └── test_csp.py                  # Unit tests
└── README.md
```

---

## How It Works

### 1. Constraint Satisfaction (CSP)

**File:** `backend/csp_solver.py`

**Hard Constraints:**
- Availability overlap (all musicians free at same time)
- Group size (3-6 musicians)
- Rhythm section (≥1 drummer or bassist)
- No double-booking

**Soft Constraints:**
- Skill compatibility: 40% weight
- Genre overlap: 40% weight
- Personality balance: 20% weight

**Algorithm:** Backtracking with forward checking

**Run it:**
```bash
python3 backend/csp_solver.py
```

### 2. Adversarial Search

**File:** `backend/adversarial_quality.py`

Models musicians with competing objectives (spotlight time, skill validation, genre comfort). Uses Nash Equilibrium: session is stable if no musician would leave (min utility > 60%).

**Quality Formula:**
```
Q = 0.4×mean(utility) + 0.4×min(utility) + 0.2×(100 - variance)
```

**Test it:**
```bash
python3 backend/adversarial_quality.py
```

### 3. A* Search

**File:** `backend/astar_grouping.py`

Finds optimal groups using four heuristics:
- Instrument synergy (30%): Balanced combinations
- Skill variance (30%): Goldilocks principle (1-3 point spread)
- Genre consensus (25%): Shared vocabulary
- Role balance (15%): 1-2 leaders optimal

**Test it:**
```bash
python3 backend/astar_grouping.py
```

---

## Running the System

### Algorithm Comparison (Main Demo)

```bash
python3 backend/csp_solver.py
```

**What it does:**
- Runs all 3 algorithms (Greedy, A*, Hybrid)
- Shows comparative results
- Displays detailed session breakdowns

**Output:**
```
======================================================================
ALGORITHM COMPARISON
======================================================================

Algorithm                      Sessions     Match Rate      Avg Quality    
----------------------------------------------------------------------
Greedy CSP                     10           54.0%           71.1%
CSP + A*                       10           37.0%           90.8%
Hybrid (A* + Adversarial)      10           37.0%           79.3%
```

### Generate Visualizations

```bash
python3 analysis/create_visualizations.py
```

Creates PNG charts in `analysis/` folder for paper.

### Run Unit Tests

```bash
python3 tests/test_csp.py
```

Validates constraint checking and solver functionality.

### Web Interface (Optional)

**Backend:**
```bash
python3 backend/api.py
```

**Frontend:**
```bash
cd frontend
python3 -m http.server 8000
# Open http://localhost:8000
```

---

## Results

| Algorithm | Sessions | Match Rate | Avg Quality | Runtime |
|-----------|----------|------------|-------------|---------|
| Greedy CSP | 10 | 54% | 71.1% | 0.8s |
| CSP + A* | 10 | 37% | 90.8% | 2.1s |
| Hybrid | 10 | 37% | 79.3% | 2.4s |

**Key Finding:** A* achieves 27.7% higher quality than greedy but matches fewer musicians, demonstrating quality-quantity tradeoff.

**Visualizations:** See `analysis/algorithm_comparison.png` and `analysis/quality_tradeoff.png`

---

## Dataset

**Source:** Synthetic (100 musicians)  
**Generation:** `python3 data/generate_dataset.py`

**Statistics:**
- Instruments: Guitar 30%, Vocals 20%, Keys 15%, Drums 10%, Bass 10%, Other 15%
- Skills: Normal distribution (μ=6, σ=2)
- Genres: 10 categories, 2-4 per musician
- Availability: 2-6 time slots from 42 windows

---

## Dependencies

```bash
pip install flask flask-cors numpy matplotlib
```

---

## Testing

```bash
python3 tests/test_csp.py
```

Tests constraint enforcement, quality scoring, and solver correctness. All tests pass.

---

## References

- Burke, E. K., et al. (1997). University timetabling using CSP
- Schaerf, A. (1999). Survey of automated timetabling
- Gusfield, D. & Irving, R. W. (1989). The Stable Marriage Problem
