"""
Route visualisation for MCVRPTW solutions.

Extracts all matplotlib rendering logic from the solver class, following the
Single Responsibility Principle.  The :class:`RouteVisualizer` is a pure
display helper; it has no dependency on the solver internals and can be
reused with any solution that exposes the same interface.
"""

from __future__ import annotations

from itertools import cycle
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt

# Colour sequence used to distinguish routes. It repeats automatically via
# itertools.cycle so the number of vehicles is not constrained.
_ROUTE_COLORS: List[str] = ["b", "g", "r", "c", "m", "y", "k"]


class RouteVisualizer:
    """Renders MCVRPTW routes and customer locations with matplotlib.

    Args:
        coordinates: Mapping ``{node_id: (x, y)}`` for all nodes including
            the depot at index 0.
        customer_demands: Mapping ``{customer_id: [qty_p0, ...]}`` used to
            annotate customers with their demand vectors when requested.
        number_of_customers: Total number of customers (excluding depot).
        dpi: Dots per inch for all generated figures (default 100).

    Example:
        >>> viz = RouteVisualizer(coordinates, demands, n_customers)
        >>> viz.display_solution(routes)
        >>> viz.display_customers()
    """

    def __init__(
        self,
        coordinates: Dict[int, Tuple[float, float]],
        customer_demands: Dict[int, List[float]],
        number_of_customers: int,
        dpi: int = 100,
    ) -> None:
        self._coords = coordinates
        self._demands = customer_demands
        self._n = number_of_customers
        self._dpi = dpi
        self._annotation_offset = self._compute_annotation_offset()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def display_customers(self) -> None:
        """Plot all customer locations and the depot without route arcs."""
        _, ax = plt.subplots(dpi=self._dpi)
        self._draw_customers(ax)
        self._draw_depot(ax)
        ax.set_aspect("equal")
        plt.show()

    def display_solution(self, routes: List[List[int]]) -> None:
        """Plot all routes of a complete solution.

        Args:
            routes: Sequence of routes, each a list of node IDs starting and
                ending with the depot (0).
        """
        _, ax = plt.subplots(dpi=self._dpi)
        self._draw_customers(ax)
        self._draw_routes(ax, routes)
        self._draw_depot(ax)
        ax.set_aspect("equal")
        plt.show()

    def display_one_route(self, route: List[int]) -> None:
        """Plot a single route on top of all customer locations.

        Args:
            route: List of node IDs starting and ending with the depot (0).
        """
        self.display_solution([route])

    def display_partial_solution(
        self,
        completed_routes: List[List[int]],
        current_route: List[int],
    ) -> None:
        """Plot completed routes plus the route currently under construction.

        Useful for debugging the step-by-step construction of the heuristic.

        Args:
            completed_routes: Routes that have already been closed.
            current_route: The route being built (not yet closed).
        """
        plt.close("all")
        _, ax = plt.subplots(dpi=self._dpi)
        all_routes = completed_routes + [current_route]
        self._draw_customers(ax)
        self._draw_routes(ax, all_routes)
        self._draw_depot(ax)
        ax.set_aspect("equal")
        plt.show()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_annotation_offset(self) -> float:
        """Return a small horizontal offset so text does not overlap points."""
        y_values = [self._coords[i][1] for i in range(self._n + 1)]
        return (max(y_values) - min(y_values)) / 60

    def _draw_customers(self, ax: plt.Axes) -> None:
        x_vals = [self._coords[i][0] for i in range(1, self._n + 1)]
        y_vals = [self._coords[i][1] for i in range(1, self._n + 1)]
        ax.scatter(x_vals, y_vals, c="steelblue", zorder=3, label="Customers")

    def _draw_depot(self, ax: plt.Axes) -> None:
        depot_x, depot_y = self._coords[0]
        ax.plot(depot_x, depot_y, c="red", marker="s", zorder=4, label="Depot")
        ax.annotate(
            "Depot",
            (depot_x + self._annotation_offset, depot_y),
            fontsize=8,
        )

    def _draw_routes(self, ax: plt.Axes, routes: List[List[int]]) -> None:
        """Draw coloured arcs for every route in *routes*."""
        depot_modulo = self._n + 1
        color_cycle = cycle(_ROUTE_COLORS)
        for route, color in zip(routes, color_cycle):
            for k in range(len(route) - 1):
                src = route[k] % depot_modulo
                dst = route[k + 1] % depot_modulo
                ax.plot(
                    [self._coords[src][0], self._coords[dst][0]],
                    [self._coords[src][1], self._coords[dst][1]],
                    c=color,
                    alpha=0.4,
                    linewidth=1.5,
                )
