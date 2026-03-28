"""
Bayesian hyperparameter optimisation for the MCVRPTW heuristic.

Uses a Gaussian-Process surrogate model (via scikit-optimize) to tune the
four Impact weights of :class:`~heuristics.MCVRPTW.MCVRPTW` with far fewer
function evaluations than a grid or random search.

Typical usage::

    from heuristics.Bayesian_optimisation import bayesian_optimisation

    result = bayesian_optimisation(
        coordinates=coords,
        customer_demands=demands,
        vehicle_parameters=vehicle_params,
        earliest_service_time=est,
        latest_service_time=lst,
        service_time=svc,
    )
    print(result["TD"], result["NV"])
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args

from .MCVRPTW import MCVRPTW
from .models import VehicleParameters

# ---------------------------------------------------------------------------
# Search-space boundaries (tuned empirically on benchmark instances)
# ---------------------------------------------------------------------------

_SEARCH_SPACE = [
    Real(0.02, 0.30, name="hyperparameter_impact1"),
    Real(0.20, 0.50, name="hyperparameter_impact2"),
    Real(0.02, 0.30, name="hyperparameter_impact3"),
    Real(0.30, 0.70, name="hyperparameter_impact4"),
]

# Optimisation budget
_N_CALLS: int = 100
_N_INITIAL_POINTS: int = 10


def bayesian_optimisation(
    coordinates: Dict[int, Any],
    customer_demands: Dict[int, List[float]],
    vehicle_parameters: VehicleParameters,
    earliest_service_time: List[float],
    latest_service_time: List[float],
    service_time: Dict[int, float],
) -> Dict[str, Any]:
    """Tune MCVRPTW Impact hyperparameters via Bayesian optimisation.

    Minimises total traveled distance over ``_N_CALLS`` solver evaluations
    using a Gaussian-Process surrogate and Expected Improvement acquisition.

    Args:
        coordinates: ``{node_id: (x, y)}`` for all nodes (0 = depot).
        customer_demands: ``{node_id: [qty_p0, ...]}`` for all nodes.
        vehicle_parameters: Vehicle configuration (see
            :class:`~heuristics.models.VehicleParameters`).
        earliest_service_time: Lower-bound arrival times (length n + 2).
        latest_service_time: Upper-bound arrival times (length n + 2).
        service_time: Service duration per customer.

    Returns:
        Dictionary with the following keys:

        - ``"TD"`` (*float*): total distance of the best solution found.
        - ``"NV"`` (*int*): number of vehicles used.
        - ``"hyperparameter_impact1"`` … ``"hyperparameter_impact4"`` (*float*):
          optimal weight values.
        - ``"time"`` (*float*): wall-clock seconds for the whole optimisation.
        - ``"delivery_time"`` (*list*): arrival times from the best run.
        - ``"needed_capacity"`` (*list*): capacity usage from the best run.
    """
    start_time = time.time()

    @use_named_args(_SEARCH_SPACE)
    def _objective(**params: float) -> float:
        """Objective: total distance traveled by the heuristic solution."""
        solver = MCVRPTW(
            coordinates=coordinates,
            customer_demands=customer_demands,
            vehicle_parameters=vehicle_parameters,
            earliest_service_time=earliest_service_time,
            latest_service_time=latest_service_time,
            service_time=service_time,
            hyperparameter_impact1=params["hyperparameter_impact1"],
            hyperparameter_impact2=params["hyperparameter_impact2"],
            hyperparameter_impact3=params["hyperparameter_impact3"],
            hyperparameter_impact4=params["hyperparameter_impact4"],
        )
        solver.heuristic()
        solver.compute_done_distance()
        return solver.Distance_done[0]

    optimisation_result = gp_minimize(
        func=_objective,
        dimensions=_SEARCH_SPACE,
        n_calls=_N_CALLS,
        n_initial_points=_N_INITIAL_POINTS,
        noise=0,
        xi=0.01,
        acq_func="EI",
        n_jobs=-1,
    )

    best_weights = dict(
        zip(
            [
                "hyperparameter_impact1",
                "hyperparameter_impact2",
                "hyperparameter_impact3",
                "hyperparameter_impact4",
            ],
            optimisation_result.x,
        )
    )

    # Re-run the heuristic with the best weights to collect the full solution.
    best_solver = MCVRPTW(
        coordinates=coordinates,
        customer_demands=customer_demands,
        vehicle_parameters=vehicle_parameters,
        earliest_service_time=earliest_service_time,
        latest_service_time=latest_service_time,
        service_time=service_time,
        hyperparameter_impact1=best_weights["hyperparameter_impact1"],
        hyperparameter_impact2=best_weights["hyperparameter_impact2"],
        hyperparameter_impact3=best_weights["hyperparameter_impact3"],
        hyperparameter_impact4=best_weights["hyperparameter_impact4"],
    )
    best_solver.heuristic()

    elapsed = time.time() - start_time

    return {
        "TD": optimisation_result.fun,
        "NV": len(best_solver.Routes),
        **best_weights,
        "time": elapsed,
        "delivery_time": best_solver.Arrival_time,
        "needed_capacity": best_solver.Capacity_related_to_Routes,
    }
