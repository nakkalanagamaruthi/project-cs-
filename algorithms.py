"""
algorithms.py
-------------
Implements three pathfinding algorithms:
  1. Dijkstra's Algorithm  – guaranteed shortest path
  2. A* Search             – heuristic-guided optimal path
  3. Greedy Best-First     – fast but not always optimal

Each function returns a result dict:
  {
    "path":          list[str]   – ordered node IDs from source to dest,
    "cost":          float       – total path cost,
    "visited_order": list[str]   – nodes popped from priority queue (exploration order),
    "log":           list[str]   – human-readable step-by-step log,
    "nodes_explored":int         – count of nodes fully processed
  }
"""

import heapq
import math


# ── Helper ────────────────────────────────────────────────────────────────────

def _reconstruct_path(came_from: dict, start: str, goal: str):
    """Walk back through came_from to build the full path."""
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    if path[0] != start:
        return []          # no valid path
    return path


# ── 1. Dijkstra's Algorithm ───────────────────────────────────────────────────

def dijkstra(graph, start: str, goal: str) -> dict:
    """
    Dijkstra's shortest-path algorithm.
    Explores nodes in order of accumulated cost from source.
    Guaranteed to find the optimal (lowest-cost) path.

    Time complexity:  O((V + E) log V)
    Space complexity: O(V)
    """
    # dist[n] = best known cost to reach n
    dist = {node: math.inf for node in graph.nodes}
    dist[start] = 0

    came_from = {start: None}
    visited_order = []
    log = [f"▶ START: {graph.node_name(start)}  →  GOAL: {graph.node_name(goal)}",
           "─" * 50]

    # Min-heap: (cost, node)
    heap = [(0, start)]

    while heap:
        cost, u = heapq.heappop(heap)

        if cost > dist[u]:          # stale entry – skip
            continue

        visited_order.append(u)
        log.append(f"  POP  [{graph.node_name(u)}]  accumulated cost = {cost:.1f}")

        if u == goal:
            log.append(f"\n✔ Goal reached!")
            break

        for v, w in graph.get_neighbors(u):
            new_cost = dist[u] + w
            if new_cost < dist[v]:
                dist[v] = new_cost
                came_from[v] = u
                heapq.heappush(heap, (new_cost, v))
                log.append(f"       ↳ relax {graph.node_name(v):12s}  new dist = {new_cost:.1f}")

    path = _reconstruct_path(came_from, start, goal)
    total = dist[goal] if dist[goal] != math.inf else -1

    log.append("─" * 50)
    if path:
        log.append(f"PATH : {' → '.join(graph.node_name(n) for n in path)}")
        log.append(f"COST : {total:.1f} km")
    else:
        log.append("No path found.")

    return {
        "path": path,
        "cost": total,
        "visited_order": visited_order,
        "log": log,
        "nodes_explored": len(visited_order)
    }


# ── 2. A* Search ──────────────────────────────────────────────────────────────

def astar(graph, start: str, goal: str) -> dict:
    """
    A* Search algorithm.
    Uses f(n) = g(n) + h(n) where:
      g(n) = actual cost from start to n
      h(n) = heuristic estimate from n to goal (Euclidean distance × scale)

    With an admissible heuristic, A* is both complete and optimal.
    Typically explores fewer nodes than Dijkstra.

    Time complexity:  O(E log V)  (heuristic-dependent)
    Space complexity: O(V)
    """
    g_score = {node: math.inf for node in graph.nodes}
    g_score[start] = 0

    came_from = {start: None}
    visited_order = []
    closed = set()
    log = [f"▶ START: {graph.node_name(start)}  →  GOAL: {graph.node_name(goal)}",
           "─" * 50]

    # Min-heap: (f_score, node)
    h0 = graph.heuristic(start, goal)
    heap = [(h0, start)]

    while heap:
        f, u = heapq.heappop(heap)

        if u in closed:
            continue
        closed.add(u)
        visited_order.append(u)

        h_u = graph.heuristic(u, goal)
        log.append(f"  POP  [{graph.node_name(u)}]  g={g_score[u]:.1f}  h={h_u:.1f}  f={f:.1f}")

        if u == goal:
            log.append(f"\n✔ Goal reached!")
            break

        for v, w in graph.get_neighbors(u):
            if v in closed:
                continue
            tentative_g = g_score[u] + w
            if tentative_g < g_score[v]:
                g_score[v] = tentative_g
                came_from[v] = u
                f_new = tentative_g + graph.heuristic(v, goal)
                heapq.heappush(heap, (f_new, v))
                log.append(f"       ↳ update {graph.node_name(v):12s}  g={tentative_g:.1f}  f={f_new:.1f}")

    path = _reconstruct_path(came_from, start, goal)
    total = g_score[goal] if g_score[goal] != math.inf else -1

    log.append("─" * 50)
    if path:
        log.append(f"PATH : {' → '.join(graph.node_name(n) for n in path)}")
        log.append(f"COST : {total:.1f} km")
    else:
        log.append("No path found.")

    return {
        "path": path,
        "cost": total,
        "visited_order": visited_order,
        "log": log,
        "nodes_explored": len(visited_order)
    }


# ── 3. Greedy Best-First Search ───────────────────────────────────────────────

def greedy_best_first(graph, start: str, goal: str) -> dict:
    """
    Greedy Best-First Search.
    Always expands the node with the smallest heuristic h(n).
    Fast and memory-efficient, but NOT guaranteed to find the optimal path.
    Included for performance comparison.

    Time complexity:  O(E log V)  (best case near O(d) with good heuristic)
    Space complexity: O(V)
    """
    came_from = {start: None}
    visited_order = []
    visited = set()
    log = [f"▶ START: {graph.node_name(start)}  →  GOAL: {graph.node_name(goal)}",
           "─" * 50]

    # Min-heap: (heuristic, node)
    h0 = graph.heuristic(start, goal)
    heap = [(h0, start)]

    # Track cost for reporting (greedy doesn't optimise cost)
    g_cost = {start: 0}

    while heap:
        h, u = heapq.heappop(heap)

        if u in visited:
            continue
        visited.add(u)
        visited_order.append(u)

        log.append(f"  POP  [{graph.node_name(u)}]  h={h:.1f}  (greedy pick)")

        if u == goal:
            log.append(f"\n✔ Goal reached!")
            break

        for v, w in graph.get_neighbors(u):
            if v not in visited:
                h_v = graph.heuristic(v, goal)
                heapq.heappush(heap, (h_v, v))
                if v not in came_from:
                    came_from[v] = u
                    g_cost[v] = g_cost[u] + w
                log.append(f"       ↳ enqueue {graph.node_name(v):12s}  h={h_v:.1f}")

    path = _reconstruct_path(came_from, start, goal)
    total = g_cost.get(goal, -1) if path else -1

    log.append("─" * 50)
    if path:
        log.append(f"PATH : {' → '.join(graph.node_name(n) for n in path)}")
        log.append(f"COST : {total:.1f} km  ⚠ may not be optimal")
    else:
        log.append("No path found.")

    return {
        "path": path,
        "cost": total,
        "visited_order": visited_order,
        "log": log,
        "nodes_explored": len(visited_order)
    }
