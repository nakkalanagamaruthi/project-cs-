"""
graph.py
--------
Manages graph creation, edge management, and node coordinates.
Represents a weighted undirected graph of cities with real-world-like connections.
"""

import math


class Graph:
    """
    Weighted undirected graph using adjacency list representation.
    Each node has (x, y) coordinates used for heuristics in A*.
    """

    def __init__(self):
        self.nodes = {}        # node_id -> {"name": str, "x": float, "y": float}
        self.edges = {}        # node_id -> list of (neighbor_id, weight)

    def add_node(self, node_id: str, name: str, x: float, y: float):
        """Add a city node with display coordinates."""
        self.nodes[node_id] = {"name": name, "x": x, "y": y}
        self.edges[node_id] = []

    def add_edge(self, u: str, v: str, weight: float):
        """Add a bidirectional weighted edge between two nodes."""
        self.edges[u].append((v, weight))
        self.edges[v].append((u, weight))

    def get_neighbors(self, node_id: str):
        """Return list of (neighbor_id, weight) for a given node."""
        return self.edges.get(node_id, [])

    def heuristic(self, a: str, b: str) -> float:
        """
        Euclidean distance heuristic between two nodes.
        Used by A* Search to estimate remaining cost.
        """
        ax, ay = self.nodes[a]["x"], self.nodes[a]["y"]
        bx, by = self.nodes[b]["x"], self.nodes[b]["y"]
        return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2) * 1.5  # scaled factor

    def node_name(self, node_id: str) -> str:
        """Return the display name of a node."""
        return self.nodes[node_id]["name"]

    def get_position(self, node_id: str):
        """Return (x, y) canvas coordinates of a node."""
        return self.nodes[node_id]["x"], self.nodes[node_id]["y"]


def build_default_graph() -> Graph:
    """
    Constructs a graph of 12 Indian cities with approximate distances.
    Weights represent approximate driving distances (km).
    """
    g = Graph()

    # ── Nodes (id, display_name, canvas_x, canvas_y) ──────────────────────────
    g.add_node("DEL", "Delhi",      380,  50)
    g.add_node("JAI", "Jaipur",     250, 130)
    g.add_node("LKO", "Lucknow",    520, 140)
    g.add_node("AMD", "Ahmedabad",  140, 250)
    g.add_node("BHO", "Bhopal",     380, 260)
    g.add_node("CCU", "Kolkata",    760, 270)
    g.add_node("BOM", "Mumbai",     120, 370)
    g.add_node("PNQ", "Pune",       180, 400)
    g.add_node("HYD", "Hyderabad",  420, 380)
    g.add_node("BLR", "Bengaluru",  320, 480)
    g.add_node("MAA", "Chennai",    480, 460)
    g.add_node("COK", "Kochi",      260, 530)

    # ── Edges (u, v, weight in km) ────────────────────────────────────────────
    g.add_edge("DEL", "JAI",  280)
    g.add_edge("DEL", "LKO",  550)
    g.add_edge("JAI", "AMD",  680)
    g.add_edge("JAI", "BHO",  600)
    g.add_edge("LKO", "BHO",  600)
    g.add_edge("LKO", "CCU", 1000)
    g.add_edge("AMD", "BOM",  530)
    g.add_edge("AMD", "BHO",  580)
    g.add_edge("BHO", "HYD",  850)
    g.add_edge("BHO", "CCU", 1300)
    g.add_edge("BOM", "PNQ",  150)
    g.add_edge("BOM", "BLR",  980)
    g.add_edge("PNQ", "HYD",  560)
    g.add_edge("PNQ", "BLR",  840)
    g.add_edge("HYD", "BLR",  570)
    g.add_edge("HYD", "MAA",  630)
    g.add_edge("HYD", "CCU", 1500)
    g.add_edge("CCU", "MAA", 1670)
    g.add_edge("BLR", "MAA",  350)
    g.add_edge("BLR", "COK",  530)
    g.add_edge("MAA", "COK",  690)

    return g
