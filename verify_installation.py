#!/usr/bin/env python3
"""
Test Script for MCVRPTW Interfaces

Verifies that all interfaces are working correctly.
Run this to ensure your installation is complete.
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("✓ Checking Python version...")
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 8:
        print(f"  ✓ Python {version_info.major}.{version_info.minor}.{version_info.micro}")
        return True
    else:
        print(f"  ✗ Python 3.8+ required (found {version_info.major}.{version_info.minor})")
        return False


def check_imports():
    """Check that all required packages are installed."""
    print("\n✓ Checking required packages...")
    
    packages = {
        'pandas': 'data processing',
        'numpy': 'numerical computing',
        'matplotlib': 'visualization',
        'streamlit': 'web interface',
        'skopt': 'hyperparameter tuning',
    }
    
    missing = []
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package:20} ({description})")
        except ImportError:
            print(f"  ✗ {package:20} (MISSING)")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_datasets():
    """Check that benchmark datasets exist."""
    print("\n✓ Checking datasets...")
    
    dataset_dir = Path(__file__).parent / "Dataset" / "benchmarking_dataset"
    
    if not dataset_dir.exists():
        print(f"  ✗ Dataset directory not found: {dataset_dir}")
        return False
    
    csv_files = list(dataset_dir.glob("dataset*.csv"))
    print(f"  ✓ Found {len(csv_files)} benchmark datasets")
    
    if len(csv_files) > 0:
        print(f"    Examples: {', '.join([f.stem.replace('dataset', '') for f in csv_files[:5]])}...")
    
    return len(csv_files) > 0


def check_heuristics_module():
    """Check that heuristics module is importable."""
    print("\n✓ Checking heuristics module...")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from heuristics import MCVRPTW
        print(f"  ✓ MCVRPTW class imported successfully")
        
        from heuristics.models import SolverResult, VehicleParameters
        print(f"  ✓ Data models imported successfully")
        
        from heuristics.visualizer import RouteVisualizer
        print(f"  ✓ RouteVisualizer imported successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Error importing heuristics: {e}")
        return False


def check_interface_files():
    """Check that interface files exist."""
    print("\n✓ Checking interface files...")
    
    files = {
        'interface.py': 'Web interface (Streamlit)',
        'cli.py': 'Command-line interface',
        'GETTING_STARTED.md': 'Quick start guide',
        'README_INTERFACE.md': 'Interface documentation',
    }
    
    all_exist = True
    for filename, description in files.items():
        filepath = Path(__file__).parent / filename
        if filepath.exists():
            print(f"  ✓ {filename:25} ({description})")
        else:
            print(f"  ✗ {filename:25} (MISSING)")
            all_exist = False
    
    return all_exist


def check_solver_basic():
    """Run a basic solver check."""
    print("\n✓ Testing solver with small example...")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from heuristics import MCVRPTW
        
        # Tiny test problem
        coordinates = {0: (0, 0), 1: (2, 5), 2: (-3, 4)}
        customer_demands = {0: [0], 1: [10], 2: [15]}
        vehicle_params = {
            'length_capacity': 200,
            'speed': 60,
            'product_capacity': {0: 100}
        }
        earliest_times = [0, 5, 5, 0]
        latest_times = [100, 30, 30, 100]
        service_times = {0: 0, 1: 5, 2: 5}
        
        solver = MCVRPTW(
            coordinates=coordinates,
            customer_demands=customer_demands,
            vehicle_parameters=vehicle_params,
            earliest_service_time=earliest_times,
            latest_service_time=latest_times,
            service_time=service_times,
        )
        
        result = solver.solve()
        
        print(f"  ✓ Solver executed successfully")
        print(f"    - Vehicles: {result.number_of_vehicles}")
        print(f"    - Total distance: {result.total_distance:.2f}")
        print(f"    - Routes: {result.routes}")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Solver error: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results):
    """Print summary of all checks."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}  {check_name}")
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All checks passed! Your installation is ready.\n")
        print("Next steps:")
        print("  1. Run the web interface:  ./run_interface.sh")
        print("  2. Or use the CLI tool:   python3 cli.py --help")
        print("  3. Check GETTING_STARTED.md for quick start guide")
    else:
        print("\n⚠️  Some checks failed. Please address issues above.")
        print("\nTroubleshooting:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Check Python version: python3 --version")
        print("  - Verify dataset location: Dataset/benchmarking_dataset/")
    
    return all_passed


def main():
    """Run all checks."""
    print("="*60)
    print("MCVRPTW Installation Verification")
    print("="*60)
    print()
    
    results = {
        'Python Version': check_python_version(),
        'Required Packages': check_imports()[0],
        'Benchmark Datasets': check_datasets(),
        'Heuristics Module': check_heuristics_module(),
        'Interface Files': check_interface_files(),
        'Solver Test': check_solver_basic(),
    }
    
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
