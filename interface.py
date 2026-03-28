"""
MCVRPTW Web Interface - Streamlit Application

Provides an interactive web-based UI to:
  1. Select and run example benchmark datasets
  2. Upload custom CSV files with problem data
  3. Visualize routes interactively (Plotly chart + geographic map for GPS data)
  4. Export results
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from heuristics.MCVRPTW import MCVRPTW
from heuristics.models import SolverResult

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="MCVRPTW Heuristic Solver",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATASET_DIR = Path(__file__).parent / "Dataset"
BENCHMARK_DIR = DATASET_DIR / "benchmarking_dataset"

# 10 distinct route colours — hex for Plotly, RGB for pydeck
_COLORS_HEX = [
    "#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
    "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#ff7f0e",
]
_COLORS_RGB = [
    [31, 119, 180], [44, 160, 44], [214, 39, 40], [148, 103, 189], [140, 86, 75],
    [227, 119, 194], [127, 127, 127], [188, 189, 34], [23, 190, 207], [255, 127, 14],
]

# ============================================================================
# Data helpers
# ============================================================================

@st.cache_data
def load_benchmark_datasets() -> Dict[str, str]:
    if not BENCHMARK_DIR.exists():
        return {}
    files = sorted(BENCHMARK_DIR.glob("dataset*.csv"))
    return {f.stem.replace("dataset", ""): str(f) for f in files}


def parse_csv_data(filepath: str, num_customers: Optional[int] = None):
    df = pd.read_csv(filepath).dropna(subset=["Coordinates"])

    if num_customers is None:
        num_customers = len(df) - 1

    coordinates = {
        i: eval(df["Coordinates"].iloc[i])
        for i in range(num_customers + 1)
        if i < len(df)
    }

    customer_demands = {}
    for i in range(num_customers + 1):
        if i < len(df):
            v = df["Customer_demands"].iloc[i]
            customer_demands[i] = eval(v) if isinstance(v, str) else [v]

    service_time = {
        i: df["Service_time"].iloc[i]
        for i in range(num_customers + 1)
        if i < len(df)
    }

    earliest_service_time, latest_service_time = [], []
    for i in range(num_customers + 1):
        if i < len(df):
            earliest_service_time.append(eval(df["Earliest_service_time"].iloc[i])[0])
            latest_service_time.append(eval(df["Latest_service_time"].iloc[i])[0])
    earliest_service_time.append(0)
    latest_service_time.append(2000)

    vehicle_capacity = float(df["Vehicle_capacity"].dropna().iloc[0])
    num_products = len(customer_demands[1])
    product_capacity = {p: vehicle_capacity for p in range(max(num_products, 1))}

    vehicle_params = {
        "length_capacity": 20000,
        "speed": 100,
        "product_capacity": product_capacity,
    }

    return (
        coordinates, customer_demands, vehicle_params,
        earliest_service_time, latest_service_time, service_time,
    )


def run_solver(
    coordinates, customer_demands, vehicle_params,
    earliest_times, latest_times, service_times, impact_weights,
) -> SolverResult:
    solver = MCVRPTW(
        coordinates=coordinates,
        customer_demands=customer_demands,
        vehicle_parameters=vehicle_params,
        earliest_service_time=earliest_times,
        latest_service_time=latest_times,
        service_time=service_times,
        hyperparameter_impact1=impact_weights["impact1"],
        hyperparameter_impact2=impact_weights["impact2"],
        hyperparameter_impact3=impact_weights["impact3"],
        hyperparameter_impact4=impact_weights["impact4"],
    )
    return solver.solve()


# ============================================================================
# Visualisation helpers
# ============================================================================

def _looks_like_gps(coordinates: Dict) -> bool:
    """Return True if coordinates are plausibly geographic (lat/lon)."""
    xs = [v[0] for v in coordinates.values()]
    ys = [v[1] for v in coordinates.values()]
    return (
        max(abs(x) for x in xs) <= 180
        and max(abs(y) for y in ys) <= 90
        and (max(xs) - min(xs)) < 30
        and (max(ys) - min(ys)) < 30
    )


def visualize_routes_plotly(
    result: SolverResult, coordinates: Dict, num_customers: int
) -> go.Figure:
    """Interactive Plotly route chart."""
    fig = go.Figure()

    for route_idx, route in enumerate(result.routes):
        color = _COLORS_HEX[route_idx % len(_COLORS_HEX)]
        xs = [coordinates[n][0] for n in route]
        ys = [coordinates[n][1] for n in route]

        # Route line
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines",
            line=dict(color=color, width=2),
            name=f"Route {route_idx + 1}",
            legendgroup=f"r{route_idx}",
            hoverinfo="skip",
        ))

        # Customer markers with hover (exclude repeated depot)
        inner = route[1:-1]
        fig.add_trace(go.Scatter(
            x=[coordinates[n][0] for n in inner],
            y=[coordinates[n][1] for n in inner],
            mode="markers",
            marker=dict(size=10, color=color, line=dict(width=1, color="#333")),
            text=[f"Customer {n}" for n in inner],
            hovertemplate="%{text}<br>(%{x:.1f}, %{y:.1f})<extra></extra>",
            legendgroup=f"r{route_idx}",
            showlegend=False,
        ))

    # Depot
    depot_x, depot_y = coordinates[0]
    fig.add_trace(go.Scatter(
        x=[depot_x], y=[depot_y],
        mode="markers",
        marker=dict(size=18, symbol="square", color="red",
                    line=dict(width=2, color="#800000")),
        name="Depot",
        hovertemplate="Depot<br>(%{x:.1f}, %{y:.1f})<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text=(f"Route Map — {result.number_of_vehicles} vehicles · "
                  f"{result.total_distance:.1f} total distance"),
            font_size=15,
        ),
        xaxis=dict(title="X", showgrid=True, gridcolor="#eee", zeroline=False),
        yaxis=dict(title="Y", showgrid=True, gridcolor="#eee",
                   zeroline=False, scaleanchor="x"),
        plot_bgcolor="#fafafa",
        paper_bgcolor="white",
        height=600,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.01,
                    bgcolor="rgba(255,255,255,0.8)"),
        hovermode="closest",
        margin=dict(r=130),
    )
    return fig


def create_pydeck_map(result: SolverResult, coordinates: Dict):
    """Real geographic map using pydeck (only for GPS coordinates)."""
    import pydeck as pdk

    path_data = [
        {
            "path": [[coordinates[n][0], coordinates[n][1]] for n in route],
            "color": _COLORS_RGB[route_idx % len(_COLORS_RGB)] + [220],
        }
        for route_idx, route in enumerate(result.routes)
    ]

    customer_data = [
        {"lon": coordinates[i][0], "lat": coordinates[i][1], "id": i}
        for i in range(1, len(coordinates))
    ]

    depot = coordinates[0]
    view = pdk.ViewState(longitude=depot[0], latitude=depot[1], zoom=7, pitch=0)

    layers = [
        pdk.Layer(
            "PathLayer", path_data,
            get_path="path", get_color="color",
            width_scale=20, width_min_pixels=3,
        ),
        pdk.Layer(
            "ScatterplotLayer", customer_data,
            get_position="[lon, lat]",
            get_radius=400, get_fill_color=[80, 140, 255, 200],
            pickable=True, auto_highlight=True,
            tooltip={"text": "Customer {id}"},
        ),
        pdk.Layer(
            "ScatterplotLayer", [{"lon": depot[0], "lat": depot[1]}],
            get_position="[lon, lat]",
            get_radius=700, get_fill_color=[255, 50, 50, 255],
        ),
    ]

    return pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_provider="carto",
        map_style="light",
    )


def create_results_summary(result: SolverResult) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Route": i + 1,
            "Customers": len(route) - 2,
            "Sequence": " → ".join(map(str, route)),
            "Distance": round(result.distance_per_vehicle[i], 2),
            "Capacity Used": result.capacity_per_vehicle[i],
        }
        for i, route in enumerate(result.routes)
    ])


def _build_report(result: SolverResult, num_customers: int,
                  customer_demands: Dict) -> str:
    lines = [
        "MCVRPTW Solution Report", "=" * 40, "",
        "SOLUTION SUMMARY",
        f"  Vehicles:        {result.number_of_vehicles}",
        f"  Total Distance:  {result.total_distance:.2f}",
        f"  Avg / Vehicle:   {result.total_distance / result.number_of_vehicles:.2f}",
        f"  Avg / Customer:  {result.total_distance / num_customers:.2f}",
        "", "ROUTES",
    ]
    for i, route in enumerate(result.routes):
        lines += [
            f"\nRoute {i + 1}:",
            f"  Sequence: {' → '.join(map(str, route))}",
            f"  Distance: {result.distance_per_vehicle[i]:.2f}",
            f"  Customers: {len(route) - 2}",
        ]
    return "\n".join(lines)


# ============================================================================
# Main UI
# ============================================================================

def main():
    st.title("🚚 MCVRPTW Heuristic Solver")
    st.caption("Multi-Compartment Vehicle Routing Problem with Time Windows")

    # ------------------------------------------------------------------ Sidebar
    st.sidebar.header("📋 Input Data")
    input_mode = st.sidebar.radio(
        "Choose input method:", ("Example Dataset", "Upload CSV File")
    )

    if input_mode == "Example Dataset":
        benchmark_datasets = load_benchmark_datasets()
        if benchmark_datasets:
            selected = st.sidebar.selectbox(
                "Select Benchmark:", list(benchmark_datasets.keys())
            )
            if st.sidebar.button("Load Dataset"):
                try:
                    coords, demands, v_params, e_times, l_times, s_times = (
                        parse_csv_data(benchmark_datasets[selected])
                    )
                    st.session_state["problem"] = dict(
                        coordinates=coords, customer_demands=demands,
                        vehicle_params=v_params, earliest_times=e_times,
                        latest_times=l_times, service_times=s_times,
                        num_customers=len(demands) - 1, source=selected,
                    )
                    st.session_state.pop("result", None)
                    st.sidebar.success(f"✓ Loaded: {selected}")
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")
        else:
            st.sidebar.warning("No benchmark datasets found")

    else:  # Upload CSV
        uploaded = st.sidebar.file_uploader("Upload CSV:", type=["csv"])
        if uploaded:
            try:
                tmp = Path("/tmp") / uploaded.name
                tmp.write_bytes(uploaded.getbuffer())
                coords, demands, v_params, e_times, l_times, s_times = (
                    parse_csv_data(str(tmp))
                )
                st.session_state["problem"] = dict(
                    coordinates=coords, customer_demands=demands,
                    vehicle_params=v_params, earliest_times=e_times,
                    latest_times=l_times, service_times=s_times,
                    num_customers=len(demands) - 1, source=uploaded.name,
                )
                st.session_state.pop("result", None)
                st.sidebar.success("✓ CSV loaded")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

    # ------------------------------------------------------------------ Gate
    if "problem" not in st.session_state:
        st.info("👈 Load data using the sidebar to get started")
        return

    prob = st.session_state["problem"]
    coordinates     = prob["coordinates"]
    customer_demands = prob["customer_demands"]
    vehicle_params  = prob["vehicle_params"]
    earliest_times  = prob["earliest_times"]
    latest_times    = prob["latest_times"]
    service_times   = prob["service_times"]
    num_customers   = prob["num_customers"]

    # -------------------------------------------------------- Problem preview
    col_prev, col_params = st.columns([2, 1])

    with col_prev:
        st.subheader(f"📊 Problem — {prob.get('source', '')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Customers", num_customers)
        c2.metric("Products", len(customer_demands[1]))
        total_demand = sum(sum(customer_demands[i]) for i in range(1, num_customers + 1))
        c3.metric("Total Demand", f"{total_demand:.0f}")
        c4.metric("Vehicle Capacity",
                  list(vehicle_params["product_capacity"].values())[0])

        with st.expander("View first 10 rows", expanded=False):
            preview = [
                {
                    "ID": i,
                    "Coords": coordinates.get(i),
                    "Demand": customer_demands.get(i),
                    "Earliest": earliest_times[i] if i < len(earliest_times) else None,
                    "Latest": latest_times[i] if i < len(latest_times) else None,
                    "Service": service_times.get(i),
                }
                for i in range(min(11, num_customers + 1))
            ]
            st.dataframe(pd.DataFrame(preview), use_container_width=True)

    with col_params:
        st.subheader("⚙️ Impact Weights")
        st.caption(
            "Each weight controls how strongly one criterion influences which customer "
            "is inserted next. Only the **ratios** matter — weights are normalised automatically."
        )

        impact1 = st.slider(
            "Impact 1 — Time-window coverage", 0.0, 1.0, 0.1, 0.05,
            help=(
                "**Physical meaning:** penalises arriving long before a customer's "
                "opening time. A high value makes the solver avoid routes where the "
                "vehicle would sit idle at the kerb waiting for the window to open.  \n"
                "↑ Raise if drivers cannot wait and must keep moving."
            ),
        )
        impact2 = st.slider(
            "Impact 2 — Total route waiting", 0.0, 1.0, 0.2, 0.05,
            help=(
                "**Physical meaning:** cumulative idle time across *all* stops in the "
                "current route. Unlike Impact 1 (one stop), this captures the total "
                "waiting burden on the whole shift.  \n"
                "↑ Raise to minimise driver idle time across the full route."
            ),
        )
        impact3 = st.slider(
            "Impact 3 — Reachability of remaining customers", 0.0, 1.0, 0.1, 0.05,
            help=(
                "**Physical meaning:** how inserting this customer now affects the "
                "solver's ability to reach the *other* customers not yet assigned. "
                "A high value adds look-ahead, avoiding choices that strand hard-to-reach "
                "customers in later routes.  \n"
                "↑ Raise if you frequently end up with unserved customers."
            ),
        )
        impact4 = st.slider(
            "Impact 4 — Local disturbance (distance + time gap)", 0.0, 1.0, 0.6, 0.05,
            help=(
                "**Physical meaning:** combined cost of inserting a customer at a "
                "specific position — extra distance driven, delay added to subsequent "
                "stops, and shrinkage of the time buffer before the next customer's "
                "window. This is the dominant criterion by default because it directly "
                "measures route efficiency.  \n"
                "↑ Raise to prioritise short, tight routes above time-window comfort."
            ),
        )

        total = impact1 + impact2 + impact3 + impact4
        if total > 0:
            impact_weights = {
                "impact1": impact1 / total,
                "impact2": impact2 / total,
                "impact3": impact3 / total,
                "impact4": impact4 / total,
            }
            st.caption(
                f"Normalised: **{impact_weights['impact1']:.2f}** / "
                f"**{impact_weights['impact2']:.2f}** / "
                f"**{impact_weights['impact3']:.2f}** / "
                f"**{impact_weights['impact4']:.2f}**"
            )
        else:
            impact_weights = {"impact1": 0.1, "impact2": 0.2,
                              "impact3": 0.1, "impact4": 0.6}

    # ------------------------------------------------------------------ Run
    st.divider()
    _, col_btn, _ = st.columns([2, 1, 2])
    with col_btn:
        run = st.button("🚀 Run Solver", use_container_width=True)

    if run:
        with st.spinner("Solving…"):
            try:
                result = run_solver(
                    coordinates, customer_demands, vehicle_params,
                    earliest_times, latest_times, service_times, impact_weights,
                )
                st.session_state["result"] = result
                st.success("✓ Solution found!")
            except Exception as e:
                st.error(f"Solver error: {e}")
                return

    # --------------------------------------------------------------- Results
    if "result" not in st.session_state:
        return

    result = st.session_state["result"]

    st.subheader("📈 Solution")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vehicles", result.number_of_vehicles)
    c2.metric("Total Distance", f"{result.total_distance:.2f}")
    c3.metric("Avg / Vehicle",
              f"{result.total_distance / result.number_of_vehicles:.2f}")
    c4.metric("Avg / Customer", f"{result.total_distance / num_customers:.2f}")

    st.subheader("🛣️ Route Details")
    st.dataframe(create_results_summary(result), use_container_width=True)

    # Interactive route chart (always shown)
    st.subheader("🗺️ Route Visualisation")
    st.plotly_chart(
        visualize_routes_plotly(result, coordinates, num_customers),
        use_container_width=True,
    )

    # Real geographic map (only when GPS coordinates are detected)
    if _looks_like_gps(coordinates):
        st.subheader("🌍 Geographic Map")
        try:
            st.pydeck_chart(create_pydeck_map(result, coordinates),
                            use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render geographic map: {e}")

    # Export
    st.subheader("💾 Export")
    col_e1, col_e2 = st.columns(2)
    summary = create_results_summary(result)
    with col_e1:
        st.download_button(
            "Download Routes CSV", summary.to_csv(index=False),
            "mcvrptw_routes.csv", "text/csv",
        )
    with col_e2:
        st.download_button(
            "Download Full Report",
            _build_report(result, num_customers, customer_demands),
            "mcvrptw_report.txt", "text/plain",
        )


if __name__ == "__main__":
    main()
