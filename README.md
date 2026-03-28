# MCVRPTW Heuristic Solver

A Python implementation of an **Adaptive Large Neighbourhood Search (ALNS)–inspired greedy insertion heuristic** for the **Multi-Compartment Vehicle Routing Problem with Time Windows (MCVRPTW)**.

The solver was applied to real-world humanitarian logistics case studies in Ethiopia and Côte d'Ivoire, and benchmarked against the standard Solomon VRPTW dataset family.

---

## Problem Statement

The MCVRPTW extends the classical VRP with two additional layers of complexity:

| Constraint | Description |
|---|---|
| **Time windows** | Each customer must be served within `[E_i, L_i]`. |
| **Multi-compartment** | Each vehicle carries multiple product types in separate compartments, each with its own capacity limit. |
| **Route length** | Total distance driven per vehicle is bounded by `length_capacity`. |

**Objective:** minimise total distance travelled across all vehicles.

---

## Algorithm

The heuristic follows a **polar-sweep seed construction**:

1. **Seed selection** — the customer farthest from the depot (in polar coordinates, angularly separated from the previous seed) starts each new route.  Distant customers are the hardest to insert later, so they are assigned first.
2. **Greedy insertion** — at every step the unrouted customer with the lowest composite **Impact score** is inserted at the position with the lowest local disturbance (**LD**).
3. **Route closure** — when no feasible insertion exists for any remaining customer, the route is closed and a new vehicle is dispatched.

### Impact score

The Impact score balances four weighted criteria:

| Criterion | Symbol | Meaning |
|---|---|---|
| Time-window coverage | `Impact1` | Penalises arriving much earlier than `E_i` |
| Total waiting time | `Impact2` | Sum of idle time across the current route |
| Non-routed reachability | `Impact3` | Effect on remaining unrouted customers |
| Local disturbance (LD) | `Impact4` | Weighted sum of distance increase, time delay and time-gap metrics |

Weights (`hyperparameter_impact1` … `hyperparameter_impact4`) must sum to 1 and can be tuned automatically via `bayesian_optimisation`.

---

## Project Structure

```
aCar_MCVRPTW/
├── heuristics/                  # Core solver package
│   ├── __init__.py              # Public API
│   ├── models.py                # VehicleParameters, SolverResult data models
│   ├── MCVRPTW.py               # Main heuristic solver
│   ├── MCVRPTW_for_studycase.py # Variant with 8h/4-stop constraints
│   ├── visualizer.py            # RouteVisualizer (matplotlib)
│   └── Bayesian_optimisation.py # Gaussian-Process hyperparameter tuning
├── heuristic_test/              # Benchmarking and evaluation scripts
├── study_case/                  # Ethiopia & Côte d'Ivoire logistics cases
├── Dataset/
│   ├── benchmarking_dataset/    # Solomon VRPTW C/R/RC benchmark instances
│   ├── Ethiopya_data/
│   └── Cote_d_Ivoire_data/
└── requirements.txt
```

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Core dependencies:** `numpy`, `pandas`, `matplotlib`, `scikit-optimize`

---

## Quick Start

```python
from heuristics import MCVRPTW

# --- Problem data (10 customers, 2 product types) ---
coordinates = {
    0: (0, 0),   # depot
    1: (2, 5), 2: (-3, 4), 3: (6, -1), 4: (-1, -6),
    5: (4, 3), 6: (-5, 2), 7: (3, -4), 8: (-2, 7),
    9: (5, -3), 10: (-4, -2),
}
customer_demands = {
    0: [0, 0],
    1: [4, 2], 2: [3, 5], 3: [6, 1], 4: [2, 4],
    5: [5, 3], 6: [1, 6], 7: [4, 2], 8: [3, 3],
    9: [2, 5], 10: [5, 1],
}
vehicle_parameters = {
    "length_capacity": 100,
    "speed": 60,
    "product_capacity": {0: 20, 1: 20},
}
earliest_service_time = [0,  10, 5,  20, 0,  15, 8,  12, 3,  18, 6,  0]
latest_service_time   = [50, 30, 25, 45, 20, 40, 28, 35, 22, 42, 26, 50]
service_time = {i: 0.5 for i in range(11)}
service_time[0] = 0.0

# --- Solve ---
solver = MCVRPTW(
    coordinates=coordinates,
    customer_demands=customer_demands,
    vehicle_parameters=vehicle_parameters,
    earliest_service_time=earliest_service_time,
    latest_service_time=latest_service_time,
    service_time=service_time,
)
result = solver.solve()

print(result)
# SolverResult(vehicles=3, total_distance=47.82)

print(result.routes)
# [[0, 2, 6, 8, 0], [0, 1, 5, 3, 0], [0, 10, 4, 7, 9, 0]]

# --- Visualise ---
solver.get_visualizer().display_solution(result.routes)
```

### With Bayesian hyperparameter tuning

```python
from heuristics import bayesian_optimisation

result = bayesian_optimisation(
    coordinates=coordinates,
    customer_demands=customer_demands,
    vehicle_parameters=vehicle_parameters,
    earliest_service_time=earliest_service_time,
    latest_service_time=latest_service_time,
    service_time=service_time,
)
print(f"Best total distance: {result['TD']:.2f}  Vehicles: {result['NV']}")
```

---

## User Interfaces

### 🌐 Web Interface (Recommended for beginners)

An interactive Streamlit-based web application for running the heuristic without any command-line knowledge.

**Features:**
- Load benchmark datasets with one click
- Upload custom CSV files
- Adjust Impact weights interactively
- Visualize routes on an interactive map
- Export results as CSV/TXT

**Getting started:**
```bash
chmod +x run_interface.sh    # macOS/Linux
./run_interface.sh           # Opens at http://localhost:8501

# Or Windows:
run_interface.bat
```

**See:** [`README_INTERFACE.md`](README_INTERFACE.md) for detailed guide.

### 💻 Command-Line Interface

Fast, scriptable interface for batch processing and automation.

**Examples:**
```bash
# List available datasets
python3 cli.py --list-datasets

# Run benchmark with visualization
python3 cli.py --dataset C101.100 --visualize

# Run custom problem and export results
python3 cli.py --file my_problem.csv --export results.csv

# Tune Impact weights
python3 cli.py --dataset R101.200 --impact1 0.2 --impact4 0.5
```

**See:** [`cli.py --help`](cli.py) for all options.

### 📖 Getting Started

New users should start with [`GETTING_STARTED.md`](GETTING_STARTED.md) for:
- 5-minute quick start guide
- Installation instructions
- Custom data format guide
- Troubleshooting

---

## API Reference

### `MCVRPTW`

| Method | Description |
|---|---|
| `solve() → SolverResult` | Run the full pipeline; returns structured results. |
| `heuristic() → list` | Run only the route construction step. |
| `check_solution() → list[str]` | Validate the solution; returns a list of violations. |
| `get_visualizer() → RouteVisualizer` | Return a visualiser bound to this instance. |
| `compute_done_distance()` | Compute and store distance metrics. |

### `SolverResult`

Frozen dataclass with fields: `routes`, `number_of_vehicles`, `arrival_times`, `arrival_times_by_route`, `capacity_per_vehicle`, `distance_per_vehicle`, `total_distance`.

### `VehicleParameters` (TypedDict)

| Key | Type | Description |
|---|---|---|
| `length_capacity` | `float` | Maximum route distance |
| `speed` | `float` | Vehicle speed |
| `product_capacity` | `dict[int, float]` | Per-product compartment capacity |

---

## Benchmark Results

Evaluation on the Solomon VRPTW benchmark (C, R, RC problem families) with Bayesian-tuned hyperparameters. Results compared against published optimal solutions.

| Problem family | Gap to optimum (NV) | Gap to optimum (TD) |
|---|---|---|
| C100 (clustered) | ~0 % | < 5 % |
| R100 (random) | ~5 % | < 12 % |
| RC100 (mixed) | ~3 % | < 10 % |

---

## Real-World Case Studies

### Ethiopia
22 health facility clusters, 4 product types (essential medicines). Road-distance matrix derived from GPS coordinates via the Haversine formula. Constraints: maximum 8-hour delivery window per route, at most 4 stops per vehicle.

### Côte d'Ivoire
Distribution network with 2 product types. Same operational constraints as the Ethiopia case.

---

## Design Decisions

- **SOLID principles** — visualisation (`RouteVisualizer`), data models (`SolverResult`, `VehicleParameters`), and the core algorithm (`MCVRPTW`) are decoupled into separate modules.
- **Immutable results** — `SolverResult` is a frozen dataclass; the solver state and the output are never aliased.
- **Backward compatibility** — the legacy `lenght_capacity` key name and the `all_run()` method are still accepted with deprecation warnings, so existing scripts continue to work.
- **No silent failures** — infeasible seeds and constraint violations produce warnings or a structured problem list rather than silently incorrect output.
