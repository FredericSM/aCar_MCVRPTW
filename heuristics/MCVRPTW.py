"""
MCVRPTW — Multi-Compartment Vehicle Routing Problem with Time Windows

Implements an ALNS-inspired greedy insertion heuristic.  The construction
follows a polar-sweep strategy: a *seed* customer (far from the depot in
polar coordinates) opens each new route, and unrouted customers are
greedily inserted at the position that minimises a weighted composite
*Impact* score.

A new vehicle is opened whenever no feasible insertion exists for any
remaining customer in the current route.

Algorithm outline (Repoussis et al., 2006 — extended for multi-compartment):
    Step 0  Initialise.  Compute polar coordinates for all customers.
    Step 1  Select a seed customer to start a new route (farthest, angularly
            separated from the previous seed).
    Step 2  For every unrouted customer u compute Impact(u):
              a. Find all feasible insertion positions in the current route.
              b. Compute local disturbance LD(u) at each position.
              c. Choose the position with minimum LD(u).
              d. Compute global Impact(u) as a weighted sum of four criteria.
    Step 3  Insert the customer u* with minimum Impact(u*) at its best
            position.  Update arrival times and remaining capacity.
    Step 4  If a feasible insertion exists for at least one unrouted customer,
            go to Step 2.  Otherwise close the route and go to Step 1.
    Step 5  All customers served — output the solution.
"""

from __future__ import annotations

import math
import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np

from .models import SolverResult, VehicleParameters
from .visualizer import RouteVisualizer

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# Angular half-width of the exclusion window used when selecting the next
# seed customer.  A value of π/6 (30°) prevents consecutive routes from
# clustering in the same angular sector.
_DEFAULT_ANGLE_WINDOW: float = math.pi / 6

# Default weights for the four Impact criteria.  Must sum to 1.
_DEFAULT_IMPACT_WEIGHTS: Dict[str, float] = {
    "impact1": 0.1,
    "impact2": 0.2,
    "impact3": 0.1,
    "impact4": 0.6,
}

# Sentinel value assigned to customers with no feasible insertion position so
# that they are always ranked last in the Impact table.
_INFEASIBLE_IMPACT: float = 1e5

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

CustomerID = int   # Index of a customer node; 0 is always the depot.
RouteIndex = int   # Position index within a route list.


class MCVRPTW:
    """Greedy insertion heuristic for the Multi-Compartment VRPTW.

    Args:
        coordinates: Mapping ``{customer_id: (x, y)}`` for every node.
            Node 0 is the depot.
        customer_demands: Mapping ``{customer_id: [qty_p0, qty_p1, ...]}``.
            Node 0 must be present with all-zero demands.
        vehicle_parameters: Vehicle configuration.  Use the
            :class:`~heuristics.models.VehicleParameters` TypedDict::

                {
                    "length_capacity": 200.0,
                    "speed": 60.0,
                    "product_capacity": {0: 100.0, 1: 100.0},
                }

        earliest_service_time: Lower-bound arrival time for each node.
            Length must be ``n_customers + 2``: the first entry is the
            earliest depot departure and the last is a sentinel (use 0).
        latest_service_time: Upper-bound arrival time for each node.
            Same length as ``earliest_service_time``.
        service_time: Mapping ``{customer_id: duration}`` for the time
            spent servicing each customer (depot = 0).
        hyperparameter_impact1: Weight for the time-window-coverage
            criterion (default 0.1).
        hyperparameter_impact2: Weight for the total-waiting-time
            criterion (default 0.2).
        hyperparameter_impact3: Weight for the non-routed-customer-impact
            criterion (default 0.1).
        hyperparameter_impact4: Weight for the local-disturbance
            (metrics summation) criterion (default 0.6).
        distance_matrix: Optional pre-computed symmetric distance matrix
            where ``D[i][j]`` is the distance between nodes *i* and *j*.
            When ``None`` the matrix is derived from Euclidean coordinates.

    Raises:
        ValueError: If the Impact weights do not sum to 1 (within 1 × 10⁻⁶).
        ValueError: If ``coordinates`` or ``customer_demands`` are empty.

    Outputs (available after calling :meth:`solve`):
        routes:
            Each inner list is a sequence of customer IDs beginning and
            ending with 0 (depot).  E.g. ``[[0, 3, 1, 0], [0, 4, 2, 0]]``.
        arrival_times:
            Arrival time at each customer, indexed by customer ID.
        arrival_times_by_route:
            Same data arranged in route order for easy per-route inspection.
        capacity_per_vehicle:
            Total product quantities loaded on each vehicle.
        distance_per_vehicle:
            Distance travelled by each vehicle.
        total_distance:
            Sum of all per-vehicle distances (primary optimisation target).

    Example:
        >>> solver = MCVRPTW(
        ...     coordinates=coords,
        ...     customer_demands=demands,
        ...     vehicle_parameters={
        ...         "length_capacity": 200,
        ...         "speed": 60,
        ...         "product_capacity": {0: 100, 1: 100},
        ...     },
        ...     earliest_service_time=est,
        ...     latest_service_time=lst,
        ...     service_time=svc,
        ... )
        >>> result = solver.solve()
        >>> print(result)
        SolverResult(vehicles=4, total_distance=312.45)
    """

    def __init__(
        self,
        coordinates: Dict[CustomerID, Tuple[float, float]],
        customer_demands: Dict[CustomerID, List[float]],
        vehicle_parameters: VehicleParameters,
        earliest_service_time: List[float],
        latest_service_time: List[float],
        service_time: Dict[CustomerID, float],
        hyperparameter_impact1: float = _DEFAULT_IMPACT_WEIGHTS["impact1"],
        hyperparameter_impact2: float = _DEFAULT_IMPACT_WEIGHTS["impact2"],
        hyperparameter_impact3: float = _DEFAULT_IMPACT_WEIGHTS["impact3"],
        hyperparameter_impact4: float = _DEFAULT_IMPACT_WEIGHTS["impact4"],
        distance_matrix: Optional[List[List[float]]] = None,
        # Legacy alias kept for backward compatibility (typo in older versions)
        Distance: Optional[List[List[float]]] = None,
    ) -> None:
        self._validate_inputs(
            coordinates, customer_demands, vehicle_parameters,
            hyperparameter_impact1, hyperparameter_impact2,
            hyperparameter_impact3, hyperparameter_impact4,
        )

        # Handle legacy keyword argument
        if distance_matrix is None and Distance is not None:
            warnings.warn(
                "The 'Distance' parameter is deprecated; use 'distance_matrix'.",
                DeprecationWarning,
                stacklevel=2,
            )
            distance_matrix = Distance

        # Normalise the legacy misspelling so the rest of the class always uses
        # 'length_capacity' regardless of which spelling the caller used.
        if "lenght_capacity" in vehicle_parameters and "length_capacity" not in vehicle_parameters:
            warnings.warn(
                "Vehicle parameter key 'lenght_capacity' is deprecated; "
                "use 'length_capacity'.",
                DeprecationWarning,
                stacklevel=2,
            )
            vehicle_parameters = dict(vehicle_parameters)
            vehicle_parameters["length_capacity"] = vehicle_parameters.pop("lenght_capacity")

        # ---- problem dimensions ----------------------------------------
        self.number_of_customer: int = len(customer_demands) - 1
        self.number_of_products: int = len(customer_demands[1])

        # ---- input data ------------------------------------------------
        self.Coordinates = coordinates
        self.customer_demands = customer_demands
        self.Vehicle_parameters = vehicle_parameters
        self.Earliest_service_time = earliest_service_time
        self.Latest_service_time = latest_service_time
        self.Service_time = service_time

        # ---- distance matrix -------------------------------------------
        self.Distance_between_customers: List[List[float]] = (
            distance_matrix if distance_matrix is not None
            else self._compute_euclidean_distance_matrix()
        )

        # ---- customers that actually require delivery ------------------
        self.J_non_routed_customers_set: List[CustomerID] = [
            i for i in range(1, self.number_of_customer + 1)
            if sum(self.customer_demands[i]) > 0
        ]
        self.number_of_customer_with_needs: int = len(self.J_non_routed_customers_set)

        # ---- solution state (populated by heuristic) ------------------
        self.Routes: List[List[int]] = []
        self.number_of_vehicle: int = 0
        self.Capacity_related_to_Routes: List[List] = []
        self.Feasible_insertion_places: List[RouteIndex] = []

        # Arrival_time[i] = scheduled arrival time at customer i.
        # Initialised to Latest_service_time as a safe upper bound; updated
        # incrementally during construction.
        self.Arrival_time: List[float] = (
            [self.Earliest_service_time[0]]
            + [self.Latest_service_time[-1]] * self.number_of_customer
            + [max(self.Latest_service_time)]
        )
        self.Arrival_time_with_same_order_than_Routes: List[List[float]] = []
        self.Distance_done: List = [0, []]
        self.Problems: List[str] = []

        # ---- geometry helpers -----------------------------------------
        self.Barycenter: Tuple[float, float] = self._compute_barycenter()
        self.Customers_polar_coordinates_set: List = []
        self.hyperparameter_angle_window: float = _DEFAULT_ANGLE_WINDOW
        self.current_angle_for_route: float = 0.0

        # ---- hyperparameters ------------------------------------------
        self.hyperparameter_metric1: float = 1 / 3
        self.hyperparameter_metric2: float = 1 / 3
        self.hyperparameter_metric3: float = 1 / 3
        self.hyperparameter_impact1: float = hyperparameter_impact1
        self.hyperparameter_impact2: float = hyperparameter_impact2
        self.hyperparameter_impact3: float = hyperparameter_impact3
        self.hyperparameter_impact4: float = hyperparameter_impact4

    def __repr__(self) -> str:
        status = (
            f"solved, vehicles={self.number_of_vehicle}, "
            f"distance={self.Distance_done[0]:.2f}"
            if self.Routes else "unsolved"
        )
        return f"MCVRPTW(customers={self.number_of_customer}, {status})"

    # ================================================================
    # Public API
    # ================================================================

    def solve(self) -> SolverResult:
        """Run the full pipeline and return a structured result.

        Executes the heuristic, computes total distance, normalises the depot
        index in every route, and returns a :class:`~heuristics.models.SolverResult`.

        Returns:
            A frozen :class:`~heuristics.models.SolverResult` with all
            solution attributes populated.
        """
        self.heuristic()
        self.compute_done_distance()
        self.change_last_by_0()
        return SolverResult(
            routes=self.Routes,
            number_of_vehicles=self.number_of_vehicle,
            arrival_times=self.Arrival_time,
            arrival_times_by_route=self.Arrival_time_with_same_order_than_Routes,
            capacity_per_vehicle=[
                self.Capacity_related_to_Routes[i][0]
                for i in range(self.number_of_vehicle)
            ],
            distance_per_vehicle=self.Distance_done[1],
            total_distance=self.Distance_done[0],
        )

    def all_run(self) -> None:
        """Run the full pipeline and print a human-readable summary.

        .. deprecated::
            Prefer :meth:`solve` which returns a structured
            :class:`~heuristics.models.SolverResult` instead of printing.
        """
        warnings.warn(
            "all_run() is deprecated; use solve() for a structured result.",
            DeprecationWarning,
            stacklevel=2,
        )
        result = self.solve()
        print("Number of Vehicles:", result.number_of_vehicles)
        print("Routes:", result.routes)
        print(
            "Delivery time for each customer (route order):",
            result.arrival_times_by_route,
        )
        print("Products capacity needed per vehicle:", result.capacity_per_vehicle)
        print("Distance traveled per vehicle:", result.distance_per_vehicle)
        print("Total distance:", result.total_distance)

    def get_visualizer(self) -> RouteVisualizer:
        """Return a :class:`~heuristics.visualizer.RouteVisualizer` bound to this instance.

        Example:
            >>> result = solver.solve()
            >>> solver.get_visualizer().display_solution(result.routes)
        """
        return RouteVisualizer(
            coordinates=self.Coordinates,
            customer_demands=self.customer_demands,
            number_of_customers=self.number_of_customer,
        )

    def check_solution(self) -> List[str]:
        """Validate the current solution and return a list of constraint violations.

        Checks:
        - Route distance does not exceed vehicle capacity.
        - Arrival times are monotonically increasing within each route.
        - Every customer is served within its time window.
        - Product capacity is not exceeded on any route.
        - Every customer that requires delivery appears exactly once.

        Returns:
            A list of human-readable violation descriptions.  An empty list
            means the solution is feasible.
        """
        self.Problems = []
        self._check_all_is_allright()
        return self.Problems

    # ================================================================
    # Geometry helpers
    # ================================================================

    def _compute_euclidean_distance_matrix(self) -> List[List[float]]:
        """Build the Euclidean distance matrix D where D[i][j] = dist(i, j).

        Returns:
            Symmetric matrix of size ``(n+1) × (n+1)``.
        """
        n = self.number_of_customer + 1
        return [
            [
                float(np.hypot(
                    self.Coordinates[i][0] - self.Coordinates[j][0],
                    self.Coordinates[i][1] - self.Coordinates[j][1],
                ))
                for j in range(n)
            ]
            for i in range(n)
        ]

    # Legacy public alias
    def Distance(self) -> List[List[float]]:
        """Alias for :meth:`_compute_euclidean_distance_matrix` (legacy)."""
        return self._compute_euclidean_distance_matrix()

    def _compute_barycenter(self) -> Tuple[float, float]:
        """Compute the demand-weighted centroid of all customer locations.

        Returns:
            ``(mean_x, mean_y)`` weighted by total demand at each customer.
        """
        total_demand = sum(
            sum(self.customer_demands[i])
            for i in range(1, self.number_of_customer + 1)
        )
        mean_x = sum(
            sum(self.customer_demands[i]) * self.Coordinates[i][0]
            for i in range(1, self.number_of_customer + 1)
        ) / total_demand
        mean_y = sum(
            sum(self.customer_demands[i]) * self.Coordinates[i][1]
            for i in range(1, self.number_of_customer + 1)
        ) / total_demand
        return (mean_x, mean_y)

    # Legacy public alias
    def barycenter(self) -> Tuple[float, float]:
        """Alias for :meth:`_compute_barycenter` (legacy)."""
        return self._compute_barycenter()

    def depot_as_barycenter(self) -> None:
        """Override the depot coordinate with the demand-weighted centroid.

        This can improve solution quality when the depot is far from the
        customer cluster.
        """
        self.Coordinates[0] = self.Barycenter

    @staticmethod
    def _polar_angle(x: float, y: float) -> float:
        """Convert Cartesian offsets to a polar angle in ``(-π, π]``.

        Args:
            x: Horizontal offset from the reference centre.
            y: Vertical offset from the reference centre.

        Returns:
            Angle in radians in the range ``(-π, π]``.
        """
        if x == 0 and y == 0:
            return 0.0
        if x == 0:
            return math.copysign(math.pi / 2, y)
        if y == 0:
            return 0.0 if x > 0 else math.pi
        angle = math.atan(abs(y) / abs(x))
        if x > 0:
            return math.copysign(angle, y)
        # x < 0
        return math.copysign(math.pi - angle, y)

    def _to_polar(
        self,
        center: Tuple[float, float],
        point: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Return the polar coordinates of *point* relative to *center*.

        Args:
            center: Reference origin ``(x, y)``.
            point: Target point ``(x, y)``.

        Returns:
            ``(radius, angle)`` where angle is in ``(-π, π]``.
        """
        dx = point[0] - center[0]
        dy = point[1] - center[1]
        return float(np.hypot(dx, dy)), self._polar_angle(dx, dy)

    def furthest_from_the_depot(self) -> None:
        """Populate ``Customers_polar_coordinates_set`` using the depot as origin.

        Each element has the form ``[(radius, angle), customer_id]``.
        Sorting or taking the maximum of this list ranks customers by radius
        (distance from depot), which is used to choose seed customers.
        """
        self.Customers_polar_coordinates_set = [
            [self._to_polar(self.Coordinates[0], self.Coordinates[u]), u]
            for u in range(1, self.number_of_customer + 1)
        ]

    def next_seed_customer(self) -> List:
        """Select the next seed customer for a new route.

        The seed must lie outside an angular window of ±``hyperparameter_angle_window``
        around the previous seed's angle.  Among the eligible candidates the
        one with the greatest radius (farthest from depot) is chosen, since
        distant customers are the hardest to include later.

        Returns:
            Element from ``Customers_polar_coordinates_set`` in the form
            ``[(radius, angle), customer_id]``.
        """
        half_window = self.hyperparameter_angle_window
        current_angle = self.current_angle_for_route

        eligible = []
        for candidate in self.Customers_polar_coordinates_set:
            candidate_angle = candidate[0][1]
            # Wrap-around cases near ±π
            if current_angle + half_window > math.pi:
                outside_window = (
                    candidate_angle >= current_angle + half_window - 2 * math.pi
                    or candidate_angle <= current_angle - half_window
                )
            elif current_angle - half_window <= -math.pi:
                outside_window = (
                    candidate_angle >= current_angle + half_window
                    or candidate_angle <= current_angle - half_window + 2 * math.pi
                )
            else:
                outside_window = (
                    candidate_angle >= current_angle + half_window
                    or candidate_angle <= current_angle - half_window
                )
            if outside_window:
                eligible.append(candidate)

        # Fall back to global farthest if the angular constraint eliminates everyone
        pool = eligible if eligible else self.Customers_polar_coordinates_set
        return max(pool)

    # ================================================================
    # Arrival-time helpers
    # ================================================================

    def _arrival_time_after(
        self, from_customer: CustomerID, to_customer: CustomerID
    ) -> float:
        """Compute the earliest feasible arrival time at *to_customer* when
        departing from *from_customer*.

        Respects the earliest service time (``E[to]``) and accounts for the
        service duration at *from_customer*.

        Args:
            from_customer: Node just serviced.
            to_customer: Node to visit next.

        Returns:
            ``max(E[to], A[from] + S[from] + D[from][to] / speed)``
        """
        travel = (
            self.Distance_between_customers[from_customer][
                to_customer % (self.number_of_customer + 1)
            ]
            / self.Vehicle_parameters["speed"]
        )
        return max(
            self.Earliest_service_time[to_customer],
            self.Arrival_time[from_customer] + self.Service_time[from_customer] + travel,
        )

    # Legacy public alias
    def get_arrival_time_from_previous_customer(
        self, previous_customer: CustomerID, current_customer: CustomerID
    ) -> float:
        """Alias for :meth:`_arrival_time_after` (legacy)."""
        return self._arrival_time_after(previous_customer, current_customer)

    def update_arrival_time(self, after_index: RouteIndex, route: List[int]) -> None:
        """Propagate shifted arrival times forward from position *after_index*.

        Called after inserting a new customer to keep ``Arrival_time``
        consistent for every subsequent stop on the route.

        Args:
            after_index: The index in *route* at which the new customer was
                inserted.  All nodes from ``route[after_index + 1]`` onward
                are recalculated.
            route: The route being modified (in-place).
        """
        for idx in range(after_index, len(route) - 2):
            self.Arrival_time[route[idx + 1]] = max(
                self.Earliest_service_time[route[idx + 1]],
                self.Arrival_time[route[idx]]
                + self.Service_time[route[idx]]
                + self.Distance_between_customers[route[idx]][route[idx + 1]]
                / self.Vehicle_parameters["speed"],
            )

    def update_Arrival_time_with_same_order_than_Routes(self) -> None:
        """Rebuild ``Arrival_time_with_same_order_than_Routes`` from current state.

        The last entry of each route (the return to depot) is computed
        explicitly rather than looked up because the depot arrival time is
        not stored in ``Arrival_time``.
        """
        self.Arrival_time_with_same_order_than_Routes = []
        for route in self.Routes:
            times = [self.Arrival_time[node] for node in route]
            last_customer = route[-2]
            times[-1] = (
                times[-2]
                + self.Service_time[last_customer]
                + self.Distance_between_customers[last_customer][route[0]]
                / self.Vehicle_parameters["speed"]
            )
            self.Arrival_time_with_same_order_than_Routes.append(times)

    # ================================================================
    # Capacity helpers
    # ================================================================

    def _check_product_capacity(
        self, customer: CustomerID, route: List[int]
    ) -> bool:
        """Return ``True`` if inserting *customer* keeps all product loads feasible.

        Args:
            customer: Candidate customer to insert.
            route: Current route (used implicitly via
                ``Capacity_related_to_Routes[-1]``).

        Returns:
            ``True`` when the capacity constraint is satisfied for every
            product type.
        """
        for product in range(self.number_of_products):
            current_load = self.Capacity_related_to_Routes[-1][0][product]
            added_demand = self.customer_demands[customer][product]
            capacity = self.Vehicle_parameters["product_capacity"][product]
            if current_load + added_demand > capacity:
                return False
        return True

    # Legacy public alias
    def check_products_constraints(
        self, customer: CustomerID, route: List[int]
    ) -> bool:
        """Alias for :meth:`_check_product_capacity` (legacy)."""
        return self._check_product_capacity(customer, route)

    def update_Capacity_related_to_Routes(
        self, insertion_index: RouteIndex, customer: CustomerID, route: List[int]
    ) -> None:
        """Update product loads and distance for the current vehicle after insertion.

        Args:
            insertion_index: Position in *route* after which *customer* is
                inserted (i.e. between ``route[insertion_index]`` and
                ``route[insertion_index + 1]``).
            customer: Customer being inserted.
            route: Current route list.
        """
        depot_modulo = self.number_of_customer + 1
        prev_node = route[insertion_index]
        next_node = route[insertion_index + 1] % depot_modulo

        for product in range(self.number_of_products):
            self.Capacity_related_to_Routes[-1][0][product] += (
                self.customer_demands[customer][product]
            )

        added_distance = (
            self.Distance_between_customers[prev_node][customer]
            + self.Distance_between_customers[next_node][customer]
            - self.Distance_between_customers[prev_node][next_node]
        )
        self.Capacity_related_to_Routes[-1][1] += added_distance

    # ================================================================
    # Feasibility check for insertion positions
    # ================================================================

    def update_Feasible_insertion_places(
        self, customer: CustomerID, route: List[int]
    ) -> None:
        """Populate ``Feasible_insertion_places`` with all valid positions for *customer* in *route*.

        An insertion between ``route[k]`` and ``route[k+1]`` is feasible when:

        1. The vehicle can reach *customer* before its latest service time.
        2. Adding *customer* keeps all product loads within capacity.
        3. Inserting *customer* does not push any subsequent node past its
           latest service time.
        4. The total route distance remains within ``length_capacity``.

        Args:
            customer: Candidate customer to insert (not yet in the route).
            route: Current (partial) route list including depot sentinels.
        """
        self.Feasible_insertion_places = []
        depot_modulo = self.number_of_customer + 1
        max_distance = self.Vehicle_parameters["length_capacity"]

        for idx in range(len(route) - 1):
            # ---- time feasibility at the insertion position ----------------
            arrival_at_customer = self._arrival_time_after(route[idx], customer)
            if arrival_at_customer > self.Latest_service_time[customer]:
                continue

            # ---- product capacity ----------------------------------------
            if not self._check_product_capacity(customer, route):
                continue

            # ---- route distance constraint --------------------------------
            next_node = route[idx + 1] % depot_modulo
            detour = (
                self.Distance_between_customers[route[idx]][customer]
                + self.Distance_between_customers[next_node][customer]
                - self.Distance_between_customers[route[idx]][next_node]
            )
            if self.Capacity_related_to_Routes[-1][1] + detour > max_distance:
                continue

            # ---- time propagation for subsequent stops --------------------
            # Compute the time delay delta caused by inserting the customer,
            # then verify that no downstream node would miss its deadline.
            prev_node = route[idx]
            arrival_at_prev = self.Arrival_time[prev_node]

            arrival_at_customer_via_prev = max(
                self.Earliest_service_time[customer],
                arrival_at_prev
                + self.Service_time[prev_node]
                + self.Distance_between_customers[customer][prev_node]
                / self.Vehicle_parameters["speed"],
            )
            arrival_at_next_via_customer = max(
                self.Earliest_service_time[next_node],
                arrival_at_customer_via_prev
                + self.Service_time[customer]
                + self.Distance_between_customers[customer][next_node]
                / self.Vehicle_parameters["speed"],
            )
            arrival_at_next_direct = max(
                self.Earliest_service_time[next_node],
                arrival_at_prev
                + self.Service_time[prev_node]
                + self.Distance_between_customers[prev_node][next_node]
                / self.Vehicle_parameters["speed"],
            )
            time_delay = arrival_at_next_via_customer - arrival_at_next_direct

            all_downstream_feasible = all(
                time_delay
                <= self.Latest_service_time[route[k]] - self.Arrival_time[route[k]]
                for k in range(idx + 1, len(route) - 1)
            )
            if all_downstream_feasible:
                self.Feasible_insertion_places.append(idx)

    # ================================================================
    # Metric functions  (local disturbance of a single insertion)
    # ================================================================

    def metric1_distance_increase(
        self,
        customer: CustomerID,
        predecessor: CustomerID,
        successor: CustomerID,
    ) -> float:
        """Extra distance incurred by inserting *customer* between *predecessor* and *successor*.

        Implements the Clark & Wright savings-based distance criterion c₁.

        Args:
            customer: Customer to insert.
            predecessor: Node immediately before the insertion point.
            successor: Node immediately after the insertion point.

        Returns:
            ``D[predecessor][customer] + D[customer][successor] - D[predecessor][successor]``
        """
        return (
            self.Distance_between_customers[predecessor][customer]
            + self.Distance_between_customers[customer][successor]
            - self.Distance_between_customers[predecessor][successor]
        )

    def metric2_time_delay(
        self,
        customer: CustomerID,
        predecessor: CustomerID,
        successor: CustomerID,
    ) -> float:
        """Marginal time delay imposed on *successor* by inserting *customer*.

        Implements criterion c₂ — the additional time the successor must wait
        compared to direct service.

        Args:
            customer: Customer to insert.
            predecessor: Node immediately before the insertion point.
            successor: Node immediately after the insertion point.

        Returns:
            Marginal time delay at *successor* (may be negative when the
            insertion reduces waiting).
        """
        return (
            self._arrival_time_after(predecessor, customer)
            + self.Service_time[customer]
            + (
                self.Distance_between_customers[customer][successor]
                - self.Distance_between_customers[predecessor][successor]
            )
            / self.Vehicle_parameters["speed"]
            - self.Arrival_time[predecessor]
            - self.Service_time[predecessor]
        )

    def metric3_time_gap(
        self,
        customer: CustomerID,
        predecessor: CustomerID,
        successor: CustomerID,
    ) -> float:
        """Time slack remaining at *customer*'s deadline after insertion.

        Implements criterion c₃ — a positive value indicates comfortable
        time-window compatibility; a negative value means infeasibility.

        Args:
            customer: Customer to insert.
            predecessor: Node immediately before the insertion point.
            successor: Unused — kept for a uniform signature with the other
                metric functions.

        Returns:
            ``L[customer] - (A[predecessor] + S[predecessor] + D[predecessor][customer] / speed)``
        """
        travel = (
            self.Distance_between_customers[predecessor][customer]
            / self.Vehicle_parameters["speed"]
        )
        return (
            self.Latest_service_time[customer]
            - (self.Arrival_time[predecessor] + self.Service_time[predecessor] + travel)
        )

    # ================================================================
    # Impact functions  (global insertion score across all candidates)
    # ================================================================

    def Impact1_time_window_coverage(
        self, customer: CustomerID, predecessor: CustomerID
    ) -> float:
        """Penalise early arrivals at *customer* (time-window coverage criterion).

        A small value means the vehicle arrives close to the customer's
        earliest allowed service time, which is preferred.

        Args:
            customer: Candidate customer.
            predecessor: The node that immediately precedes the insertion point.

        Returns:
            ``A[predecessor] + S[predecessor] + D[customer][predecessor] / speed - E[customer]``
        """
        travel = (
            self.Distance_between_customers[customer][predecessor]
            / self.Vehicle_parameters["speed"]
        )
        return (
            self.Arrival_time[predecessor]
            + self.Service_time[predecessor]
            + travel
            - self.Earliest_service_time[customer]
        )

    def Impact2_total_waiting_time(
        self, customer: CustomerID, route: List[int]
    ) -> float:
        """Sum of waiting times across all currently-assigned stops in *route*.

        A vehicle waits at stop *i* when it arrives before ``E[i]``.  The
        total waiting time is a proxy for schedule slack.

        Args:
            customer: Candidate customer (used for context only; waiting time
                is computed over the existing route stops).
            route: Current route under construction.

        Returns:
            ``∑ max(0, E[i] - A[i])`` for all stops *i* in *route*.
        """
        return sum(
            max(0.0, self.Earliest_service_time[i] - self.Arrival_time[i])
            for i in route
        )

    def Impact3_non_routed_customers(self, customer: CustomerID) -> float:
        """Measure how inserting *customer* reduces the reachability of other unrouted customers.

        Encourages clustering by favouring insertions that keep the remaining
        unrouted customers reachable.

        Args:
            customer: Candidate customer being evaluated.

        Returns:
            Average over all other unrouted customers *j* of
            ``max(L[j] - E[customer] - D[customer][j] / speed,
                  L[customer] - E[j] - D[customer][j] / speed)``.
            Returns 0.0 when *customer* is the last unrouted customer.
        """
        remaining = self.J_non_routed_customers_set
        if len(remaining) <= 1:
            return 0.0

        total = sum(
            max(
                self.Latest_service_time[j]
                - self.Earliest_service_time[customer]
                - self.Distance_between_customers[customer][j]
                / self.Vehicle_parameters["speed"],
                self.Latest_service_time[customer]
                - self.Earliest_service_time[j]
                - self.Distance_between_customers[customer][j]
                / self.Vehicle_parameters["speed"],
            )
            for j in remaining
            if j != customer
        )
        return total / (len(remaining) - 1)

    def Impact4_metrics_summation(
        self,
        customer: CustomerID,
        predecessor: CustomerID,
        successor: CustomerID,
    ) -> float:
        """Weighted sum of the three local disturbance metrics for one insertion position.

        Args:
            customer: Candidate customer.
            predecessor: Node before the insertion point.
            successor: Node after the insertion point.

        Returns:
            ``w₁·c₁ + w₂·c₂ + w₃·c₃`` where ``wₖ`` are the metric
            hyperparameters (each 1/3 by default).
        """
        return (
            self.hyperparameter_metric1 * self.metric1_distance_increase(customer, predecessor, successor)
            + self.hyperparameter_metric2 * self.metric2_time_delay(customer, predecessor, successor)
            + self.hyperparameter_metric3 * self.metric3_time_gap(customer, predecessor, successor)
        )

    # ================================================================
    # Utility methods
    # ================================================================

    def get_number_of_customer_in_Routes(self) -> int:
        """Return the total number of customers currently assigned to routes."""
        return sum(len(route) - 2 for route in self.Routes)

    def compute_done_distance(self) -> None:
        """Compute and store total distance and per-vehicle distances.

        Populates ``Distance_done[0]`` (total) and ``Distance_done[1]``
        (list of per-vehicle distances).
        """
        depot_modulo = self.number_of_customer + 1
        self.Distance_done[1] = [
            sum(
                self.Distance_between_customers[route[i]][
                    route[i + 1] % depot_modulo
                ]
                for i in range(len(route) - 1)
            )
            for route in self.Routes
        ]
        self.Distance_done[0] = sum(self.Distance_done[1])

    def change_last_by_0(self) -> None:
        """Normalise the last element of every route to 0 (depot index).

        During construction the depot return is encoded as
        ``number_of_customer + 1`` to distinguish it from the depot departure.
        This method replaces that sentinel with 0 for a cleaner output.
        """
        depot_modulo = self.number_of_customer + 1
        for route in self.Routes:
            route[-1] = route[-1] % depot_modulo

    # ================================================================
    # Core heuristic
    # ================================================================

    def heuristic(self) -> List[List[int]]:
        """Execute the ALNS-inspired greedy insertion heuristic.

        Constructs a solution by iteratively opening routes, selecting seed
        customers, and inserting the unrouted customer with the lowest Impact
        score at its least-disturbing feasible position.

        The six-step algorithm is described in the class docstring.

        Returns:
            The constructed set of routes (same object as ``self.Routes``).
        """
        # Step 0 — compute polar coordinates for all customers (used for
        #           seed selection).
        self.furthest_from_the_depot()

        needs_new_route = True
        seed_customer = [[0.0, 0.0], 0]

        while self.J_non_routed_customers_set:
            # ---- Step 1: open a new route with a seed customer -----------
            if needs_new_route:
                self.current_angle_for_route += seed_customer[0][1]
                if self.current_angle_for_route > math.pi:
                    self.current_angle_for_route -= 2 * math.pi

                seed_customer = self.next_seed_customer()

                # Skip seeds that have already been assigned to a route.
                while seed_customer[1] not in self.J_non_routed_customers_set:
                    self.Customers_polar_coordinates_set = [
                        c for c in self.Customers_polar_coordinates_set
                        if c[1] != seed_customer[1]
                    ]
                    seed_customer = self.next_seed_customer()

                seed_id: CustomerID = seed_customer[1]
                route = [0, seed_id, self.number_of_customer + 1]
                initial_capacity = [
                    self.customer_demands[seed_id][p]
                    for p in range(self.number_of_products)
                ]
                self.Capacity_related_to_Routes.append(
                    [initial_capacity, 2 * self.Distance_between_customers[0][seed_id]]
                )
                self.J_non_routed_customers_set.remove(seed_id)

                self.Arrival_time[seed_id] = max(
                    self.Earliest_service_time[seed_id],
                    self.Arrival_time[0]
                    + self.Distance_between_customers[0][seed_id]
                    / self.Vehicle_parameters["speed"],
                )
                if self.Arrival_time[seed_id] > self.Latest_service_time[seed_id]:
                    warnings.warn(
                        f"Vehicle is too slow to reach customer {seed_id} "
                        f"within its time window.",
                        RuntimeWarning,
                        stacklevel=2,
                    )

            # ---- Step 6: all customers served ---------------------------
            if not self.J_non_routed_customers_set:
                self.Routes.append(route)
                self.update_Arrival_time_with_same_order_than_Routes()
                self.number_of_vehicle = len(self.Routes)
                return self.Routes

            # ---- Step 2: compute Impact score for each candidate --------
            impact_scores: List[Tuple[float, int, CustomerID]] = []

            for candidate in self.J_non_routed_customers_set:
                self.update_Feasible_insertion_places(candidate, route)

                if not self.Feasible_insertion_places:
                    impact_scores.append((_INFEASIBLE_IMPACT, 0, candidate))
                    continue

                # Step 2b: local disturbances at each feasible position.
                local_disturbances = [
                    self.Impact4_metrics_summation(
                        candidate,
                        route[pos],
                        route[pos + 1] % (self.number_of_customer + 1),
                    )
                    for pos in self.Feasible_insertion_places
                ]

                # Step 2c: best insertion position minimises local disturbance.
                best_local_idx = local_disturbances.index(min(local_disturbances))
                best_insertion_pos = self.Feasible_insertion_places[best_local_idx]

                avg_local_disturbance = sum(local_disturbances) / len(local_disturbances)

                # Step 2g: composite Impact score.
                score = (
                    self.hyperparameter_impact1
                    * self.Impact1_time_window_coverage(candidate, route[best_insertion_pos])
                    + self.hyperparameter_impact2
                    * self.Impact2_total_waiting_time(candidate, route)
                    + self.hyperparameter_impact3
                    * self.Impact3_non_routed_customers(candidate)
                    + self.hyperparameter_impact4 * avg_local_disturbance
                )
                impact_scores.append((score, best_insertion_pos, candidate))

            # ---- Step 3: insert the best candidate ----------------------
            best_score, best_pos, best_customer = min(impact_scores)

            if best_score == _INFEASIBLE_IMPACT:
                # No candidate can be inserted — close the route.
                self.Routes.append(route)
                needs_new_route = True
                continue

            self.J_non_routed_customers_set.remove(best_customer)
            self.update_Capacity_related_to_Routes(best_pos, best_customer, route)
            route.insert(best_pos + 1, best_customer)
            self.update_arrival_time(best_pos, route)

            # ---- Step 6 (early): if this was the last customer, terminate.
            if not self.J_non_routed_customers_set:
                self.Routes.append(route)
                self.update_Arrival_time_with_same_order_than_Routes()
                self.number_of_vehicle = len(self.Routes)
                return self.Routes

            # ---- Step 4: check whether another insertion is still possible.
            # update_Feasible_insertion_places mutates self.Feasible_insertion_places;
            # we call it for each remaining customer and stop as soon as one is feasible.
            any_feasible = False
            for u in self.J_non_routed_customers_set:
                self.update_Feasible_insertion_places(u, route)
                if self.Feasible_insertion_places:
                    any_feasible = True
                    break

            if not any_feasible:
                # No more insertions possible in this route — close it (Step 5 → Step 1).
                self.Routes.append(route)
                needs_new_route = True
            else:
                needs_new_route = False

        self.update_Arrival_time_with_same_order_than_Routes()
        self.number_of_vehicle = len(self.Routes)
        return self.Routes

    # ================================================================
    # Solution validation
    # ================================================================

    def _check_all_is_allright(self) -> None:
        """Internal implementation of constraint checking (see :meth:`check_solution`)."""
        routed_count = 0
        depot_modulo = self.number_of_customer + 1

        for route in self.Routes:
            routed_count += len(route) - 2

            # Distance constraint
            route_distance = sum(
                self.Distance_between_customers[route[i]][route[i + 1] % depot_modulo]
                for i in range(len(route) - 1)
            )
            if route_distance > self.Vehicle_parameters["length_capacity"]:
                msg = (
                    f"Route {self.Routes.index(route)}: distance {route_distance:.2f} "
                    f"exceeds length_capacity {self.Vehicle_parameters['length_capacity']}."
                )
                self.Problems.append(msg)

            # Monotone arrival times
            delays = [
                self.Arrival_time[route[i]] - self.Arrival_time[route[i + 1]]
                for i in range(len(route) - 2)
            ]
            if max(delays) > 0:
                self.Problems.append(
                    f"Route {self.Routes.index(route)}: arrival times are not monotone."
                )

            # Time-window constraints
            route_capacity = [0.0] * self.number_of_products
            for customer in route[1:-1]:
                a_time = self.Arrival_time[customer]
                if not (
                    self.Earliest_service_time[customer]
                    <= a_time
                    <= self.Latest_service_time[customer]
                ):
                    self.Problems.append(
                        f"Customer {customer}: arrival {a_time:.2f} outside "
                        f"[{self.Earliest_service_time[customer]}, "
                        f"{self.Latest_service_time[customer]}]."
                    )
                for product in range(self.number_of_products):
                    route_capacity[product] += self.customer_demands[customer][product]

            # Product capacity (per route)
            for product in range(self.number_of_products):
                limit = self.Vehicle_parameters["product_capacity"][product]
                if route_capacity[product] > limit:
                    self.Problems.append(
                        f"Route {self.Routes.index(route)}: product {product} load "
                        f"{route_capacity[product]:.2f} exceeds capacity {limit}."
                    )

        # All customers with demand must appear exactly once
        if routed_count != self.number_of_customer_with_needs:
            self.Problems.append(
                f"Routed customers ({routed_count}) ≠ "
                f"customers with demand ({self.number_of_customer_with_needs})."
            )

        for customer in self.J_non_routed_customers_set:
            appearances = sum(customer in route for route in self.Routes)
            if appearances != 1:
                self.Problems.append(
                    f"Customer {customer} appears {appearances} times across routes "
                    f"(expected exactly 1)."
                )

    # ================================================================
    # Input validation
    # ================================================================

    @staticmethod
    def _validate_inputs(
        coordinates: Dict,
        customer_demands: Dict,
        vehicle_parameters: Dict,
        w1: float, w2: float, w3: float, w4: float,
    ) -> None:
        """Raise ``ValueError`` if any input invariant is violated."""
        if not coordinates:
            raise ValueError("'coordinates' must not be empty.")
        if not customer_demands:
            raise ValueError("'customer_demands' must not be empty.")
        weight_sum = w1 + w2 + w3 + w4
        if abs(weight_sum - 1.0) > 1e-6:
            raise ValueError(
                f"Impact hyperparameters must sum to 1.0, got {weight_sum:.6f}."
            )
        # Support both old (lenght_capacity) and new (length_capacity) key names
        has_length = (
            "length_capacity" in vehicle_parameters
            or "lenght_capacity" in vehicle_parameters
        )
        if not has_length:
            raise ValueError(
                "'vehicle_parameters' must contain 'length_capacity'."
            )
        if "speed" not in vehicle_parameters:
            raise ValueError("'vehicle_parameters' must contain 'speed'.")
        if "product_capacity" not in vehicle_parameters:
            raise ValueError("'vehicle_parameters' must contain 'product_capacity'.")
