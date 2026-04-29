"""
main.py
-------
Entry point for the Route Optimizer application.

Run with:
    python main.py

Requirements: Python 3.8+  (tkinter included in standard library)
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from graph import build_default_graph
from visualizer import GraphVisualizer


def main():
    print("=" * 60)
    print("  ROUTE OPTIMIZER — Pathfinding Algorithm Visualizer")
    print("=" * 60)
    print("  Algorithms: Dijkstra | A* | Greedy Best-First")
    print("  Graph     : 12 cities, 22 weighted edges")
    print("  Starting UI...")
    print("=" * 60)

    graph = build_default_graph()

    print(f"\n  Loaded {len(graph.nodes)} nodes, "
          f"{sum(len(v) for v in graph.edges.values()) // 2} edges.\n")

    app = GraphVisualizer(graph)
    app.run()


if __name__ == "__main__":
    main()
