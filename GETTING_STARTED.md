# Getting Started with MCVRPTW Heuristic Solver

## 🚀 Quick Start (5 minutes)

### Option 1: Web Interface (Recommended for beginners)

```bash
# macOS / Linux
chmod +x run_interface.sh
./run_interface.sh

# Windows
run_interface.bat
```

Then:
1. Browse to `http://localhost:8501`
2. Select "Example Dataset" → "Benchmark - Solomon"
3. Pick a dataset (e.g., "C101")
4. Click "Load Example Dataset"
5. Click "🚀 Run Solver"
6. View results and visualization!

### Option 2: Command-Line Interface (For automation)

```bash
# List available datasets
python3 cli.py --list-datasets

# Run a benchmark dataset
python3 cli.py --dataset C101.100

# Run with visualization
python3 cli.py --dataset C101.100 --visualize

# Upload custom problem
python3 cli.py --file my_problem.csv --export results.csv
```

### Option 3: Python Script (For development)

```python
from heuristics import MCVRPTW

# Load your problem data
coordinates = {0: (0, 0), 1: (2, 5), 2: (-3, 4)}
customer_demands = {0: [0], 1: [10], 2: [15]}
vehicle_params = {
    'length_capacity': 200,
    'speed': 60,
    'product_capacity': {0: 100}
}
# ... (see README.md for full example)

# Solve
solver = MCVRPTW(
    Coordinates=coordinates,
    Customer_demands=customer_demands,
    Vehicle_parameters=vehicle_params,
    # ... other parameters
)
result = solver.solve()

# Results available:
print(f"Vehicles: {result.number_of_vehicles}")
print(f"Total Distance: {result.total_distance}")
print(f"Routes: {result.routes}")
```

---

## 📋 File Guide

| File | Purpose |
|------|---------|
| `interface.py` | Web interface (Streamlit) |
| `cli.py` | Command-line tool |
| `run_interface.sh` | Start script (macOS/Linux) |
| `run_interface.bat` | Start script (Windows) |
| `heuristics/MCVRPTW.py` | Core solver |
| `Dataset/benchmarking_dataset/` | Benchmark test cases |
| `README_INTERFACE.md` | Detailed interface guide |
| `README.md` | Algorithm documentation |

---

## 🛠 Installation

### Prerequisites
- Python 3.8+
- macOS, Linux, or Windows

### Manual Setup
```bash
# Navigate to project
cd aCar_MCVRPTW

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt

# Run one of the interfaces:
# Web:
python3 -m streamlit run interface.py
# Or CLI:
python3 cli.py --help
```

---

## 📊 Example: Run a Benchmark & Visualize

```bash
# CLI approach
python3 cli.py --dataset R101.100 --visualize

# This will:
# 1. Load the R101 dataset with 100 customers
# 2. Run the solver
# 3. Display the solution metrics
# 4. Show a route visualization map
```

---

## 💾 Custom Data Format

If you have your own routing problem, create a CSV file with these columns:

```csv
Coordinates,Customer_demands,Earliest_service_time,Latest_service_time,Service_time,Vehicle_capacity
"(42.0, 66.0)","[10.0]","[65.0]","[146.0]",90.0,200.0
"(45.0, 68.0)","[30.0]","[912.0]","[967.0]",90.0,
"(42.0, 70.0)","[20.0]","[825.0]","[870.0]",90.0,
```

Then run:
```bash
# Web interface: Upload via sidebar
# Or CLI:
python3 cli.py --file my_problem.csv --visualize --export results.csv
```

---

## ❓ Troubleshooting

### "Command not found"
- Use `python3` instead of `python` on macOS/Linux
- Make sure you activated the virtual environment

### "ModuleNotFoundError: pandas"
```bash
pip install pandas numpy matplotlib scikit-optimize streamlit
```

### Web interface won't open
- Check that port 8501 is available
- Try accessing http://localhost:8501 manually
- Check terminal for error messages

### Solver is slow
- This is normal for large problems (200+ customers)
- Try a smaller example dataset first
- Large problems may take 10-30 seconds

---

## 📖 Next Steps

1. **Try examples**: Use the web interface to explore benchmark datasets
2. **Tune parameters**: Adjust Impact weights to see how solution changes
3. **Custom problems**: Prepare your own CSV data and run solver
4. **Export results**: Download routes and reports for analysis
5. **Integrate**: Use the Python API in your own applications

---

## 🔗 Resources

- **Main README**: See `README.md` for algorithm details
- **Interface Guide**: See `README_INTERFACE.md` for detailed feature walkthrough
- **Datasets**: Over 50 benchmark problems in `Dataset/benchmarking_dataset/`
- **Code**: All solver code in `heuristics/` package

---

## 👥 Support

For issues or questions:
1. Check error messages in terminal
2. Review README files for your use case
3. Inspect sample CSV files in `Dataset/`
4. Try with a smaller dataset to isolate problems

Happy routing! 🚚✨
