"""
MCVRPTW Web Interface - Streamlit Application

Provides an interactive web-based UI to:
  1. Select and run example benchmark datasets
  2. Upload custom CSV files with problem data
  3. Visualize routes and solution metrics
  4. Export results
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
from typing import Dict, List, Tuple, Optional
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from heuristics.MCVRPTW import MCVRPTW
from heuristics.visualizer import RouteVisualizer
from heuristics.models import SolverResult

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="MCVRPTW Heuristic Solver",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATASET_DIR = Path(__file__).parent / "Dataset"
BENCHMARK_DIR = DATASET_DIR / "benchmarking_dataset"
CASE_STUDIES_DIR = DATASET_DIR / "Cote_d_Ivoire_data"  # Alternative: "Ethiopya_data"

# ============================================================================
# Utility Functions
# ============================================================================

@st.cache_data
def load_benchmark_datasets() -> Dict[str, str]:
    """Load list of available benchmark datasets."""
    if not BENCHMARK_DIR.exists():
        return {}
    
    files = sorted(BENCHMARK_DIR.glob("dataset*.csv"))
    return {f.stem.replace("dataset", ""): str(f) for f in files}


@st.cache_data
def load_case_study_datasets() -> Dict[str, str]:
    """Load list of available case study datasets."""
    datasets = {}
    
    # Côte d'Ivoire data
    ci_dir = DATASET_DIR / "Cote_d_Ivoire_data"
    if ci_dir.exists():
        datasets["Côte d'Ivoire"] = str(ci_dir)
    
    # Ethiopia data
    et_dir = DATASET_DIR / "Ethiopya_data"
    if et_dir.exists():
        datasets["Ethiopia"] = str(et_dir)
    
    return datasets


def parse_csv_data(filepath: str, num_customers: Optional[int] = None) -> Tuple[Dict, Dict, Dict, List, List, Dict]:
    """
    Parse CSV file and extract problem data.
    
    Args:
        filepath: Path to CSV file
        num_customers: Number of customers (if None, infer from file)
    
    Returns:
        Tuple of (coordinates, customer_demands, vehicle_params, 
                  earliest_times, latest_times, service_times)
    """
    df = pd.read_csv(filepath)
    
    if num_customers is None:
        num_customers = len(df) - 1
    
    # Extract coordinates
    coordinates = {}
    for i in range(num_customers + 1):
        if i < len(df):
            coordinates[i] = eval(df['Coordinates'][i])
    
    # Extract demands (support both single and multi-product)
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


def run_solver(coordinates: Dict, customer_demands: Dict, vehicle_params: Dict,
               earliest_times: List, latest_times: List, service_times: Dict,
               impact_weights: Optional[Dict] = None) -> SolverResult:
    """Run MCVRPTW solver with given parameters."""
    
    if impact_weights is None:
        impact_weights = {
            'impact1': 0.1,
            'impact2': 0.2,
            'impact3': 0.1,
            'impact4': 0.6,
        }
    
    solver = MCVRPTW(
        Coordinates=coordinates,
        Customer_demands=customer_demands,
        Vehicle_parameters=vehicle_params,
        Earliest_service_time=earliest_times,
        Latest_service_time=latest_times,
        Service_time=service_times,
        hyperparameter_impact1=impact_weights['impact1'],
        hyperparameter_impact2=impact_weights['impact2'],
        hyperparameter_impact3=impact_weights['impact3'],
        hyperparameter_impact4=impact_weights['impact4'],
    )
    
    return solver.solve()


def visualize_routes(result: SolverResult, coordinates: Dict, 
                     customer_demands: Dict, num_customers: int) -> plt.Figure:
    """Create visualization of routes."""
    
    visualizer = RouteVisualizer(
        coordinates=coordinates,
        customer_demands=customer_demands,
        number_of_customers=num_customers,
    )
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    # Draw customers and routes
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
    ax.set_title(f'MCVRPTW Solution - {result.number_of_vehicles} Vehicles', fontsize=14, fontweight='bold')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    
    return fig


def create_results_summary(result: SolverResult, coordinates: Dict) -> pd.DataFrame:
    """Create a summary table of routes and metrics."""
    
    summary_data = []
    
    for route_idx, route in enumerate(result.routes):
        distance = result.distance_per_vehicle[route_idx]
        capacity = result.capacity_per_vehicle[route_idx]
        
        summary_data.append({
            'Route': route_idx + 1,
            'Customers': len(route) - 2,  # Exclude depot at start and end
            'Customer Sequence': ' → '.join(map(str, route)),
            'Distance': f"{distance:.2f}",
            'Capacity Used': capacity if isinstance(capacity, (int, float)) else str(capacity),
        })
    
    df = pd.DataFrame(summary_data)
    return df


# ============================================================================
# Streamlit UI
# ============================================================================

def main():
    st.title("🚚 MCVRPTW Heuristic Solver")
    st.markdown("""
    **Multi-Compartment Vehicle Routing Problem with Time Windows**
    
    An adaptive large-neighbourhood search (ALNS)-inspired greedy insertion heuristic 
    for solving complex routing problems with time constraints and multi-product requirements.
    """)
    
    # ====================================================================
    # Sidebar - Input Selection
    # ====================================================================
    
    st.sidebar.header("📋 Input Data")
    input_mode = st.sidebar.radio(
        "Choose input method:",
        ("Example Dataset", "Upload CSV File", "Manual Input")
    )
    
    data_loaded = False
    coordinates = None
    customer_demands = None
    vehicle_params = None
    earliest_times = None
    latest_times = None
    service_times = None
    num_customers = None
    
    # --- Example Dataset Mode ---
    if input_mode == "Example Dataset":
        st.sidebar.subheader("Available Datasets")
        
        dataset_type = st.sidebar.selectbox(
            "Dataset Category:",
            ("Benchmark - Solomon", "Case Studies")
        )
        
        if dataset_type == "Benchmark - Solomon":
            benchmark_datasets = load_benchmark_datasets()
            if benchmark_datasets:
                selected_dataset = st.sidebar.selectbox(
                    "Select Benchmark:",
                    list(benchmark_datasets.keys())
                )
                
                if st.sidebar.button("Load Example Dataset"):
                    try:
                        filepath = benchmark_datasets[selected_dataset]
                        (coordinates, customer_demands, vehicle_params,
                         earliest_times, latest_times, service_times) = parse_csv_data(filepath)
                        num_customers = len(customer_demands) - 1
                        data_loaded = True
                        st.sidebar.success(f"✓ Loaded: {selected_dataset}")
                    except Exception as e:
                        st.sidebar.error(f"Error loading dataset: {e}")
            else:
                st.sidebar.warning("No benchmark datasets found")
        else:
            case_studies = load_case_study_datasets()
            if case_studies:
                selected_case = st.sidebar.selectbox(
                    "Select Case Study:",
                    list(case_studies.keys())
                )
                st.sidebar.info("Case study datasets require special handling. "
                               "Please see documentation for format details.")
            else:
                st.sidebar.warning("No case study datasets found")
    
    # --- Upload CSV Mode ---
    elif input_mode == "Upload CSV File":
        st.sidebar.subheader("Upload CSV Data")
        uploaded_file = st.sidebar.file_uploader(
            "Upload problem CSV file:",
            type=['csv']
        )
        
        if uploaded_file:
            try:
                # Save to temporary location
                temp_file = Path("/tmp") / uploaded_file.name
                temp_file.write_bytes(uploaded_file.getbuffer())
                
                (coordinates, customer_demands, vehicle_params,
                 earliest_times, latest_times, service_times) = parse_csv_data(str(temp_file))
                num_customers = len(customer_demands) - 1
                data_loaded = True
                st.sidebar.success("✓ CSV loaded successfully")
            except Exception as e:
                st.sidebar.error(f"Error parsing CSV: {e}")
    
    # --- Manual Input Mode ---
    elif input_mode == "Manual Input":
        st.sidebar.subheader("Manual Problem Configuration")
        
        num_customers_manual = st.sidebar.number_input(
            "Number of customers:",
            min_value=1,
            max_value=500,
            value=10
        )
        
        st.sidebar.info(
            "Manual input mode is under development. "
            "For now, please use Example or Upload modes."
        )
    
    # ====================================================================
    # Main Content - Problem Preview & Solver
    # ====================================================================
    
    if data_loaded and coordinates and customer_demands:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Problem Preview")
            
            # Display problem statistics
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            
            with col_stats1:
                st.metric("Customers", num_customers)
            
            with col_stats2:
                num_products = len(customer_demands[1])
                st.metric("Products", num_products)
            
            with col_stats3:
                total_demand = sum(
                    sum(customer_demands[i]) 
                    for i in range(1, num_customers + 1)
                )
                st.metric("Total Demand", f"{total_demand:.1f}")
            
            with col_stats4:
                st.metric("Vehicle Duration", f"{vehicle_params.get('length_capacity', 'N/A')}")
            
            # Show sample data
            with st.expander("View Problem Data (First 10 Customers)", expanded=False):
                data_preview = []
                for i in range(min(10, num_customers + 1)):
                    data_preview.append({
                        'Customer ID': i,
                        'Coordinates': str(coordinates.get(i, 'N/A')),
                        'Demand': str(customer_demands.get(i, 'N/A')),
                        'Earliest': earliest_times[i] if i < len(earliest_times) else 'N/A',
                        'Latest': latest_times[i] if i < len(latest_times) else 'N/A',
                        'Service Time': service_times.get(i, 'N/A'),
                    })
                st.dataframe(pd.DataFrame(data_preview), use_container_width=True)
        
        with col2:
            st.subheader("⚙️ Solver Parameters")
            
            impact1 = st.slider(
                "Impact 1 (Time Window)",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.05
            )
            
            impact2 = st.slider(
                "Impact 2 (Waiting Time)",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05
            )
            
            impact3 = st.slider(
                "Impact 3 (Reachability)",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.05
            )
            
            impact4 = st.slider(
                "Impact 4 (Disturbance)",
                min_value=0.0,
                max_value=1.0,
                value=0.6,
                step=0.05
            )
            
            # Normalize weights
            total_weight = impact1 + impact2 + impact3 + impact4
            if total_weight > 0:
                impact_weights = {
                    'impact1': impact1 / total_weight,
                    'impact2': impact2 / total_weight,
                    'impact3': impact3 / total_weight,
                    'impact4': impact4 / total_weight,
                }
                st.info(f"Total weight: {total_weight:.2f} (normalized)")
            else:
                impact_weights = {'impact1': 0.1, 'impact2': 0.2, 'impact3': 0.1, 'impact4': 0.6}
        
        # ====================================================================
        # Run Solver
        # ====================================================================
        
        st.divider()
        
        col_run1, col_run2, col_run3 = st.columns([1, 1, 1])
        
        with col_run2:
            if st.button("🚀 Run Solver", key="run_solver", use_container_width=True):
                
                with st.spinner("Solving... This may take a moment"):
                    try:
                        result = run_solver(
                            coordinates=coordinates,
                            customer_demands=customer_demands,
                            vehicle_params=vehicle_params,
                            earliest_times=earliest_times,
                            latest_times=latest_times,
                            service_times=service_times,
                            impact_weights=impact_weights
                        )
                        
                        st.session_state.last_result = result
                        st.session_state.last_coordinates = coordinates
                        st.session_state.last_customer_demands = customer_demands
                        st.session_state.last_num_customers = num_customers
                        st.success("✓ Solution found!")
                        
                    except Exception as e:
                        st.error(f"Solver error: {e}")
        
        # ====================================================================
        # Display Results
        # ====================================================================
        
        if 'last_result' in st.session_state:
            result = st.session_state.last_result
            
            st.subheader("📈 Solution Results")
            
            # Results metrics
            col_res1, col_res2, col_res3, col_res4 = st.columns(4)
            
            with col_res1:
                st.metric("Vehicles Used", result.number_of_vehicles)
            
            with col_res2:
                st.metric("Total Distance", f"{result.total_distance:.2f}")
            
            with col_res3:
                avg_distance = result.total_distance / result.number_of_vehicles
                st.metric("Avg Distance/Vehicle", f"{avg_distance:.2f}")
            
            with col_res4:
                if num_customers > 0:
                    st.metric("Distance/Customer", f"{result.total_distance / num_customers:.2f}")
            
            # Routes summary
            st.subheader("🛣️ Route Details")
            routes_summary = create_results_summary(result, coordinates)
            st.dataframe(routes_summary, use_container_width=True)
            
            # Visualization
            st.subheader("🗺️ Route Visualization")
            
            try:
                fig = visualize_routes(
                    result,
                    coordinates,
                    customer_demands,
                    num_customers
                )
                st.pyplot(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Visualization error: {e}")
            
            # Export results
            st.subheader("💾 Export Results")
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                csv = routes_summary.to_csv(index=False)
                st.download_button(
                    label="Download Routes as CSV",
                    data=csv,
                    file_name="mcvrptw_routes.csv",
                    mime="text/csv"
                )
            
            with col_exp2:
                # Create detailed results file
                results_text = f"""MCVRPTW Solution Report
====================

PROBLEM SUMMARY
---------------
Number of Customers: {num_customers}
Number of Products: {len(customer_demands[1])}
Total Demand: {sum(sum(customer_demands[i]) for i in range(1, num_customers + 1)):.2f}

SOLUTION SUMMARY
----------------
Number of Vehicles: {result.number_of_vehicles}
Total Distance: {result.total_distance:.2f}
Average Distance per Vehicle: {result.total_distance / result.number_of_vehicles:.2f}
Average Distance per Customer: {result.total_distance / num_customers:.2f}

ROUTES
------
"""
                for idx, route in enumerate(result.routes):
                    results_text += f"\nRoute {idx + 1}:\n"
                    results_text += f"  Sequence: {' → '.join(map(str, route))}\n"
                    results_text += f"  Distance: {result.distance_per_vehicle[idx]:.2f}\n"
                    results_text += f"  Customers: {len(route) - 2}\n"
                
                st.download_button(
                    label="Download Full Report",
                    data=results_text,
                    file_name="mcvrptw_report.txt",
                    mime="text/plain"
                )
    
    else:
        st.info("👈 Load data using the sidebar to get started")


if __name__ == "__main__":
    main()
