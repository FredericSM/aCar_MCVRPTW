# MCVRPTW Heuristic Solver - Web Interface

A modern web-based interface for running the Multi-Compartment Vehicle Routing Problem with Time Windows (MCVRPTW) heuristic solver.

## Features

- **🚀 Easy-to-use web interface** - No command-line knowledge needed
- **📊 Example datasets** - Run pre-loaded Solomon benchmark datasets instantly
- **📁 Custom file upload** - Load your own problem instances as CSV files
- **⚙️ Parameter tuning** - Adjust Impact weights interactively
- **🗺️ Route visualization** - Beautiful maps showing optimized routes
- **💾 Export results** - Download routes and reports as CSV/TXT

## Quick Start

### Prerequisites
- Python 3.8 or higher
- macOS, Linux, or Windows

### Installation & Running

#### macOS / Linux
```bash
# Make the script executable
chmod +x run_interface.sh

# Run the interface
./run_interface.sh
```

#### Windows
```bash
# Simply double-click run_interface.bat
# Or from Command Prompt:
run_interface.bat
```

#### Manual Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the interface
streamlit run interface.py
```

The interface will open automatically at **http://localhost:8501**

## How to Use

### 1. Load Problem Data

#### Option A: Run Example Dataset
1. Select "Example Dataset" in the sidebar
2. Choose "Benchmark - Solomon"
3. Pick a dataset (e.g., "C101", "R101", "RC101")
4. Click "Load Example Dataset"

#### Option B: Upload Custom CSV
1. Select "Upload CSV File" in the sidebar
2. Upload your CSV file with the following columns:
   - `Coordinates`: Tuple coordinates as string, e.g., `"(40.0, 50.0)"`
   - `Customer_demands`: List of demands, e.g., `"[10.0, 5.0]"`
   - `Earliest_service_time`: Earliest arrival time, e.g., `"[912.0]"`
   - `Latest_service_time`: Latest arrival time, e.g., `"[967.0]"`
   - `Service_time`: Time to service customer, e.g., `90.0`
   - `Vehicle_capacity`: Max capacity per compartment, e.g., `200.0`

### 2. Preview Problem

Once data is loaded, the interface shows:
- **Problem statistics**: Number of customers, products, total demand
- **Vehicle parameters**: Duration capacity, speed
- **Data preview**: First 10 customers with their details

### 3. Adjust Solver Parameters

Fine-tune the Impact weights for different optimization objectives:

| Parameter | Default | Meaning |
|-----------|---------|---------|
| **Impact 1** | 0.1 | Penalizes arriving much earlier than time window start |
| **Impact 2** | 0.2 | Minimizes total waiting time in route |
| **Impact 3** | 0.1 | Affects reachability of remaining customers |
| **Impact 4** | 0.6 | Local disturbance (distance, time delay, time gaps) |

**Note**: Weights are automatically normalized to sum to 1.0.

### 4. Run Solver

Click the **"🚀 Run Solver"** button to solve the problem.

Processing time depends on problem size:
- 100 customers: ~1-2 seconds
- 200+ customers: ~5-30 seconds

### 5. View Results

After solving, the interface displays:
- **Solution metrics**:
  - Number of vehicles used
  - Total distance traveled
  - Average distance per vehicle
  - Average distance per customer
  
- **Route details table**:
  - Route number
  - Customers in each route
  - Distance and capacity used per route
  
- **Route visualization**:
  - Map showing all routes in different colors
  - Depot marked as red square
  - Customers marked as blue circles
  - Connections between customers

### 6. Export Results

Download your results:
- **CSV export**: Route details table as CSV
- **Full report**: Complete text report with problem summary and all routes

## Input CSV Format

Your custom CSV file should look like this:

```
Coordinates,Customer_demands,Earliest_service_time,Latest_service_time,Service_time,Vehicle_capacity
"(40.0, 50.0)","[0.0]","[0.0]","[1236.0]",0.0,200.0
"(45.0, 68.0)","[10.0]","[912.0]","[967.0]",90.0,
"(45.0, 70.0)","[30.0]","[825.0]","[870.0]",90.0,
"(42.0, 66.0)","[10.0]","[65.0]","[146.0]",90.0,
```

**Important notes**:
- First row (index 0) is always the **depot**
- Depot must have zero demands
- Lists (demands, times) use Python list syntax with square brackets
- Coordinates use Python tuple syntax with parentheses
- All numeric values in matching units (e.g., distances in km, speeds in km/h)

## Example Datasets

The interface includes pre-loaded Solomon benchmark datasets:

### Categories
- **C-sets** (Clustered): Customers grouped geographically
- **R-sets** (Random): Customers randomly distributed
- **RC-sets** (Mixed): Mix of clustered and random

### Naming Convention
- `C101.100` = Solomon C class, 100 customers
- `R103.200` = Solomon R class, 200 customers
- `RC104.100` = Solomon RC class, 100 customers

Available sizes: 100, 200, 300+ customers depending on dataset.

## Interpretation of Results

### Solution Quality Metrics

**Total Distance**: 
- Lower is better
- Primary optimization objective

**Number of Vehicles**:
- Affected by vehicle capacity and time window constraints
- Minimize by increasing vehicle capacity or relaxing time windows

**Route Balance**:
- Uneven distribution suggests bottleneck customers
- Consider adjusting Impact weights to favor reachability (Impact 3)

### Route Visualization

- **Route color** indicates which vehicle serves which customers
- **Route length** (line density) shows vehicle utilization
- **Clustering patterns** suggest if geographic distribution is well-optimized
- **Time window conflicts** may cause inefficient routes (check latest times)

## Tips for Best Results

1. **Verify input data**:
   - Ensure all coordinates are reasonable (no extreme outliers)
   - Check time windows aren't too restrictive
   - Confirm vehicle capacity matches demand levels

2. **Tune solver parameters**:
   - Higher **Impact 4** (0.7+): Optimize for distance
   - Higher **Impact 2** (0.3+): Minimize waiting time
   - Higher **Impact 3** (0.2+): Better customer reachability

3. **Handle infeasibility**:
   - If "Solver error" occurs, check:
     - Vehicle capacity is sufficient for all demands
     - Latest service times allow enough routing time
     - Coordinates are valid (not duplicates at origin)

## Troubleshooting

### "Error loading dataset"
- Check that benchmark datasets exist in `Dataset/benchmarking_dataset/`
- Verify dataset file is readable

### "CSV parsing error"
- Ensure coordinates are strings like `"(x, y)"` (with quotes)
- Ensure demands are strings like `"[d1, d2]"` (with quotes)
- Check that all required columns are present

### "Solver error: ..."
- Verify time windows are feasible (latest ≥ earliest)
- Ensure vehicle capacity > max single-customer demand
- Check that coordinates are numeric (not NaN)

### Interface is slow or unresponsive
- This is normal for large problems (200+ customers)
- Solver typically completes in <30 seconds
- Try with smaller dataset if testing interface

## Performance Notes

- **Small problems** (50-100 customers): <1 second
- **Medium problems** (100-200 customers): 1-10 seconds
- **Large problems** (200+ customers): 10-30 seconds

Processing time depends on:
- Number of customers
- Number of products (compartments)
- Tightness of time windows
- Vehicle capacity constraints

## Support for Development

For issues, feature requests, or improvements:
1. Check the main README.md for algorithm details
2. See `heuristics/MCVRPTW.py` for solver implementation
3. Review `heuristics/models.py` for data structures

## License

Same as main project. See LICENSE file.
