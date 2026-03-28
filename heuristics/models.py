"""
Data models for the MCVRPTW heuristic.

Centralises all shared types so that every module in the package works
with the same structures instead of bare dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from typing import TypedDict


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class VehicleParameters(TypedDict):
    """Configuration for a single vehicle type.

    All vehicles in a fleet share these parameters.

    Keys:
        length_capacity: Maximum total route distance the vehicle can travel
            before returning to the depot (same unit as the distance matrix).
        speed: Average travel speed used to convert distances to travel times.
        product_capacity: Mapping ``{product_id: maximum_units}`` giving the
            compartment capacity for each product type.
    """

    length_capacity: float
    speed: float
    product_capacity: Dict[int, float]


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SolverResult:
    """Immutable snapshot of a completed MCVRPTW solve.

    Attributes:
        routes: List of routes, each a list of customer IDs starting and
            ending with depot (0).  E.g. ``[[0, 3, 1, 0], [0, 4, 2, 0]]``.
        number_of_vehicles: Number of vehicles dispatched.
        arrival_times: Arrival time at each customer indexed by customer ID.
        arrival_times_by_route: Same information ordered to match ``routes``.
        capacity_per_vehicle: Product quantities loaded on each vehicle,
            indexed to match ``routes``.
        distance_per_vehicle: Distance travelled by each vehicle, indexed to
            match ``routes``.
        total_distance: Sum of all per-vehicle distances.
    """

    routes: List[List[int]]
    number_of_vehicles: int
    arrival_times: List[float]
    arrival_times_by_route: List[List[float]]
    capacity_per_vehicle: List[List[float]]
    distance_per_vehicle: List[float]
    total_distance: float

    def __repr__(self) -> str:
        return (
            f"SolverResult("
            f"vehicles={self.number_of_vehicles}, "
            f"total_distance={self.total_distance:.2f})"
        )
