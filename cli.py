#!/usr/bin/env python3
"""
MCVRPTW Command-Line Interface (CLI)

Quick command-line tool to run the MCVRPTW heuristic without a web interface.
Perfect for batch processing and scripting.

Usage:
    python3 cli.py --dataset C101.100                    # Run benchmark dataset
    python3 cli.py --file my_problem.csv                 # Run custom CSV file
    python3 cli.py --help                                # Show all options
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from heuristics.MCVRPTW import MCVRPTW
from heuristics.visualizer import RouteVisualizer


def parse_csv_data(filepath: str, num_customers: int = None):
    """Parse CSV file and extract problem data."""
    df = pd.read_csv(filepath).dropna(subset=['Coordinates'])

    if num_customers is None:
        num_customers = len(df) - 1
    
    # Extract coordinates
    coordinates = {}
    for i in range(num_customers + 1):
        if i < len(df):
            coordinates[i] = eval(df['Coordinates'][i])
    
    # Extract demands
    customer_demands = {}
    for i in range(num_customers + 1):
        if i < len(df):
            demand_str = df['Customer_demands'][i]
            if isinstance(demand_str, str):
                customer_demands[i] = eval(demand_str)
            else:
                customer_demands[i] = [demand_str]
    
    # Extract service times
    service_time = {}
    for i in range(num_customers + 1):
        if i < len(df):
            service_time[i] = df['Service_time'][i]
    
    # Extract time windows
    earliest_service_time = []
    latest_service_time = []
    for i in range(num_customers + 1):
        if i < len(df):
            earliest_service_time.append(eval(df['Earliest_service_time'][i])[0])
            latest_service_time.append(eval(df['Latest_service_time'][i])[0])
    earliest_service_time.append(0)
    latest_service_time.append(2000)
    
    # Extract vehicle capacity
    vehicle_capacity_data = df['Vehicle_capacity'].dropna().iloc[0]
    product_capacity = {0: float(vehicle_capacity_data)}
    
    # Infer number of products from demands
    num_products = len(customer_demands[1])
    if num_products > 1:
        product_capacity = {p: float(vehicle_capacity_data) for p in range(num_products)}
    
    vehicle_params = {
        'length_capacity': 20000,
        'speed': 100,
        'product_capacity': product_capacity
    }
    
    return (coordinates, customer_demands, vehicle_params, 
            earliest_service_time, latest_service_time, service_time)


def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print("MCVRPTW Heuristic Solver - Command Line Interface")
    print("Multi-Compartment Vehicle Routing Problem with Time Windows")
    print("="*70 + "\n")


def print_results(result, coordinates, num_customers):
    """Print solution results in formatted table."""
    print("\n" + "="*70)
    print("SOLUTION RESULTS")
    print("="*70)
    print(f"\n📊 Summary Metrics:")
    print(f"  • Number of Vehicles:        {result.number_of_vehicles}")
    print(f"  • Total Distance:            {result.total_distance:.2f}")
    print(f"  • Avg Distance per Vehicle:  {result.total_distance / result.number_of_vehicles:.2f}")
    print(f"  • Avg Distance per Customer: {result.total_distance / num_customers:.2f}")
    
    print(f"\n🛣️  Route Details:")
    print("-" * 70)
    print(f"{'Route':<8} {'Customers':<12} {'Distance':<12} {'Capacity':<12}")
    print("-" * 70)
    
    for idx, route in enumerate(result.routes):
        num_customers_in_route = len(route) - 2  # Exclude depot at start and end
        distance = result.distance_per_vehicle[idx]
        capacity = result.capacity_per_vehicle[idx]
        
        print(f"{idx+1:<8} {num_customers_in_route:<12} {distance:<12.2f} {str(capacity):<12}")
    
    print("-" * 70)
    
    print(f"\n📍 Full Route Sequences:")
    print("-" * 70)
    for idx, route in enumerate(result.routes):
        route_str = " → ".join(map(str, route))
        print(f"Route {idx + 1}: {route_str}")
    
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="MCVRPTW Heuristic Solver CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run benchmark dataset
  python3 cli.py --dataset C101.100
  
  # Run custom file with visualization
  python3 cli.py --file my_problem.csv --visualize
  
  # Run with custom impact weights
  python3 cli.py --dataset R101.200 --impact1 0.2 --impact4 0.5
  
  # List all available benchmark datasets
  python3 cli.py --list-datasets
        """
    )
    
    parser.add_argument(
        "--dataset",
        help="Benchmark dataset name (e.g., C101.100, R102.200, RC103.100)"
    )
    
    parser.add_argument(
        "--file",
        help="Path to custom CSV problem file"
    )
    
    parser.add_argument(
        "--impact1",
        type=float,
        default=0.1,
        help="Impact 1 weight (time window coverage, default 0.1)"
    )
    
    parser.add_argument(
        "--impact2",
        type=float,
        default=0.2,
        help="Impact 2 weight (waiting time, default 0.2)"
    )
    
    parser.add_argument(
        "--impact3",
        type=float,
        default=0.1,
        help="Impact 3 weight (reachability, default 0.1)"
    )
    
    parser.add_argument(
        "--impact4",
        type=float,
        default=0.6,
        help="Impact 4 weight (disturbance, default 0.6)"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Display route visualization (requires matplotlib)"
    )
    
    parser.add_argument(
        "--list-datasets",
        action="store_true",
        help="List all available benchmark datasets"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        help="Export results to CSV file"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    # Handle list datasets
    if args.list_datasets:
        dataset_dir = Path(__file__).parent / "Dataset" / "benchmarking_dataset"
        if dataset_dir.exists():
            files = sorted(dataset_dir.glob("dataset*.csv"))
            print(f"📁 Available Benchmark Datasets ({len(files)} total):\n")
            
            categories = {"C": [], "R": [], "RC": []}
            for f in files:
                name = f.stem.replace("dataset", "")
                if name.startswith("C"):
                    categories["C"].append(name)
                elif name.startswith("RC"):
                    categories["RC"].append(name)
                elif name.startswith("R"):
                    categories["R"].append(name)
            
            for cat in ["C", "R", "RC"]:
                if categories[cat]:
                    print(f"  {cat}-sets: {', '.join(categories[cat][:5])}{'...' if len(categories[cat]) > 5 else ''}")
        else:
            print("❌ Dataset directory not found!")
        return
    
    # Load data
    try:
        if args.dataset:
            dataset_dir = Path(__file__).parent / "Dataset" / "benchmarking_dataset"
            filepath = dataset_dir / f"dataset{args.dataset}.csv"
            
            if not filepath.exists():
                print(f"❌ Dataset not found: {args.dataset}")
                print(f"📍 Expected location: {filepath}")
                print("💡 Use --list-datasets to see available options")
                return
            
            print(f"📂 Loading dataset: {args.dataset}")
            
        elif args.file:
            filepath = Path(args.file)
            if not filepath.exists():
                print(f"❌ File not found: {args.file}")
                return
            print(f"📂 Loading file: {args.file}")
        else:
            print("❌ Please provide either --dataset or --file")
            print("   Use --help for more information")
            return
        
        # Parse data
        print("⏳ Parsing problem data...")
        (coordinates, customer_demands, vehicle_params,
         earliest_times, latest_times, service_times) = parse_csv_data(str(filepath))
        
        num_customers = len(customer_demands) - 1
        num_products = len(customer_demands[1])
        
        print(f"✓ Problem loaded successfully")
        print(f"  • Customers: {num_customers}")
        print(f"  • Products: {num_products}")
        
        # Normalize impact weights
        total_weight = args.impact1 + args.impact2 + args.impact3 + args.impact4
        if total_weight > 0:
            impact_weights = {
                'impact1': args.impact1 / total_weight,
                'impact2': args.impact2 / total_weight,
                'impact3': args.impact3 / total_weight,
                'impact4': args.impact4 / total_weight,
            }
        else:
            impact_weights = {'impact1': 0.1, 'impact2': 0.2, 'impact3': 0.1, 'impact4': 0.6}
        
        # Solve
        print("\n⏳ Running solver...")
        start_time = time.time()
        
        solver = MCVRPTW(
            coordinates=coordinates,
            customer_demands=customer_demands,
            vehicle_parameters=vehicle_params,
            earliest_service_time=earliest_times,
            latest_service_time=latest_times,
            service_time=service_times,
            hyperparameter_impact1=impact_weights['impact1'],
            hyperparameter_impact2=impact_weights['impact2'],
            hyperparameter_impact3=impact_weights['impact3'],
            hyperparameter_impact4=impact_weights['impact4'],
        )
        
        result = solver.solve()
        elapsed_time = time.time() - start_time
        
        print(f"✓ Solution found in {elapsed_time:.2f} seconds\n")
        
        # Print results
        print_results(result, coordinates, num_customers)
        
        # Visualize if requested
        if args.visualize:
            print("📊 Generating visualization...")
            try:
                import matplotlib.pyplot as plt
                
                fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
                colors = ["b", "g", "r", "c", "m", "y", "k", "orange", "purple", "brown"]
                
                # Plot depot
                depot_x, depot_y = coordinates[0]
                ax.scatter(depot_x, depot_y, s=300, marker='s', c='red', label='Depot', zorder=5)
                
                # Plot customers
                for i in range(1, num_customers + 1):
                    x, y = coordinates[i]
                    ax.scatter(x, y, s=100, c='lightblue', edgecolors='black', zorder=3)
                    ax.annotate(str(i), (x, y), ha='center', va='center', fontsize=8, zorder=4)
                
                # Plot routes
                for route_idx, route in enumerate(result.routes):
                    color = colors[route_idx % len(colors)]
                    for i in range(len(route) - 1):
                        x1, y1 = coordinates[route[i]]
                        x2, y2 = coordinates[route[i + 1]]
                        ax.plot([x1, x2], [y1, y2], c=color, linewidth=2, alpha=0.7, zorder=2)
                
                ax.set_aspect('equal')
                ax.grid(True, alpha=0.3)
                ax.set_title(f'MCVRPTW Solution - {result.number_of_vehicles} Vehicles')
                ax.set_xlabel('X Coordinate')
                ax.set_ylabel('Y Coordinate')
                
                plt.tight_layout()
                plt.show()
                
            except ImportError:
                print("❌ Matplotlib not available. Install with: pip install matplotlib")
        
        # Export if requested
        if args.export:
            print(f"\n💾 Exporting results to {args.export}...")
            
            export_data = []
            for idx, route in enumerate(result.routes):
                export_data.append({
                    'Route': idx + 1,
                    'Customers': len(route) - 2,
                    'Customer_Sequence': ' → '.join(map(str, route)),
                    'Distance': result.distance_per_vehicle[idx],
                    'Capacity_Used': result.capacity_per_vehicle[idx],
                })
            
            df = pd.DataFrame(export_data)
            df.to_csv(args.export, index=False)
            print(f"✓ Results exported successfully")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
