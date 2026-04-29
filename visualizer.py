"""
visualizer.py
-------------
Premium dark-themed visualization engine for Route Optimizer.
Renders the graph on a tkinter Canvas with:
  • Animated node pulse on hover
  • Color-coded visited / path nodes
  • Smooth edge highlighting
  • Glowing path rendering
  • Modern sidebar with step-by-step log
"""

import tkinter as tk
from tkinter import ttk, font
import math

# ── Color Palette ─────────────────────────────────────────────────────────────
DARK_COLORS = {
    "bg":           "#28282b",   # dark matte charcoal
    "panel":        "#303034",   # slightly lighter matte panel
    "card":         "#38383d",   # matte grey card
    "border":       "#48484d",   # subtle matte border
    "accent":       "#c6796d",   # matte terracotta/clay
    "accent2":      "#6a8a9a",   # matte slate blue
    "gold":         "#c2a075",   # matte wheat/sand
    "green":        "#7c9a78",   # matte sage green
    "red":          "#b36969",   # matte brick red
    "text":         "#dfdfdf",   # soft matte white
    "text_dim":     "#8b8b92",   # muted text
    "text_mid":     "#acaeb3",   # medium text
    "node_default": "#38383d",   # default node fill
    "node_border":  "#55555c",   # default node border
    "edge":         "#55555c",   # default edge
    "edge_active":  "#c2a075",   # active edge (matte wheat)
    "edge_glow":    "#e6d4b8",   # bright inner glow
    "visited_fill": "#374235",   # visited node fill (sage tint)
    "path_fill":    "#483c2f",   # path node fill (wheat tint)
    "start_fill":   "#453030",   # start node fill (brick tint)
    "goal_fill":    "#453030",   # goal node fill
}

LIGHT_COLORS = {
    "bg":           "#f4f4f6",   # light matte grey
    "panel":        "#ebebec",   # slightly darker panel
    "card":         "#e2e2e4",   # matte card
    "border":       "#d1d1d4",   # subtle border
    "accent":       "#c6796d",   # matte terracotta
    "accent2":      "#6a8a9a",   # matte slate blue
    "gold":         "#c2a075",   # matte wheat
    "green":        "#7c9a78",   # matte sage green
    "red":          "#b36969",   # matte brick red
    "text":         "#2c2c2e",   # dark text
    "text_dim":     "#6c6c70",   # muted text
    "text_mid":     "#4c4c50",   # medium text
    "node_default": "#e2e2e4",   # default node fill
    "node_border":  "#b0b0b5",   # default node border
    "edge":         "#b0b0b5",   # default edge
    "edge_active":  "#c2a075",   # active edge (matte wheat)
    "edge_glow":    "#ffffff",   # bright inner glow
    "visited_fill": "#d0dfcd",   # visited node fill (sage light tint)
    "path_fill":    "#e5dac9",   # path node fill (wheat light tint)
    "start_fill":   "#ecd9d9",   # start node fill (brick light tint)
    "goal_fill":    "#ecd9d9",   # goal node fill
}

COLORS = dict(DARK_COLORS)

NODE_RADIUS = 24
CANVAS_W = 880
CANVAS_H = 560


class GraphVisualizer:
    """Main visualizer class. Owns the tkinter root window and all widgets."""

    def __init__(self, graph):
        self.graph = graph
        self.result = None          # current algorithm result
        self.start_node = None
        self.goal_node  = None
        self.hover_node = None
        self.log_history = []
        self.is_dark_mode = True

        self._build_window()
        self._build_ui()
        self._draw_graph()

    # ── Window Setup ──────────────────────────────────────────────────────────

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("Route Optimizer  ·  Pathfinding Visualizer")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        # Center window
        w, h = 1380, 760
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI Layout ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top Header Bar ────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=COLORS["panel"], height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Left: logo + title
        logo_frame = tk.Frame(header, bg=COLORS["panel"])
        logo_frame.pack(side="left", padx=24, pady=0)

        tk.Label(logo_frame, text="◈", font=("Courier", 22, "bold"),
                 fg=COLORS["accent"], bg=COLORS["panel"]).pack(side="left", padx=(0, 10))

        title_frame = tk.Frame(logo_frame, bg=COLORS["panel"])
        title_frame.pack(side="left")
        tk.Label(title_frame, text="ROUTE OPTIMIZER",
                 font=("Courier", 15, "bold"),
                 fg=COLORS["text"], bg=COLORS["panel"]).pack(anchor="w")
        tk.Label(title_frame, text="Pathfinding Algorithm Visualizer",
                 font=("Courier", 9),
                 fg=COLORS["text_mid"], bg=COLORS["panel"]).pack(anchor="w")

        # Right: tag badges
        badges_frame = tk.Frame(header, bg=COLORS["panel"])
        badges_frame.pack(side="right", padx=24)
        for tag, color in [("Dijkstra", "#6a8a9a"), ("A*", "#9b82a8"), ("Greedy", "#c2a075")]:
            b = tk.Label(badges_frame, text=f"  {tag}  ",
                         font=("Courier", 9, "bold"),
                         fg=color, bg=COLORS["bg"],
                         relief="flat", padx=4, pady=2)
            b.pack(side="left", padx=4)

        # Thin accent line under header
        tk.Frame(self.root, bg=COLORS["accent"], height=1).pack(fill="x")

        # ── Main Body ─────────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True)

        # Left sidebar
        self._build_left_sidebar(body)

        # Canvas area
        canvas_frame = tk.Frame(body, bg=COLORS["bg"])
        canvas_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        self._build_canvas(canvas_frame)

        # Right panel
        self._build_right_panel(body)

    def _build_left_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=COLORS["panel"], width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x")

        pad = {"padx": 18, "pady": 0}

        # Section: Source
        self._section_label(sidebar, "SOURCE NODE")
        self.src_var = tk.StringVar(value="DEL")
        self._node_dropdown(sidebar, self.src_var)

        # Section: Destination
        self._section_label(sidebar, "DESTINATION NODE")
        self.dst_var = tk.StringVar(value="BLR")
        self._node_dropdown(sidebar, self.dst_var)

        # Section: Algorithm
        self._section_label(sidebar, "ALGORITHM")
        self.algo_var = tk.StringVar(value="dijkstra")
        algo_options = [
            ("Dijkstra's Algorithm", "dijkstra"),
            ("A* Search",            "astar"),
            ("Greedy Best-First",    "greedy"),
        ]
        for label, val in algo_options:
            self._radio_btn(sidebar, label, val)

        # Run button
        tk.Frame(sidebar, bg=COLORS["bg"], height=16).pack(fill="x")
        run_btn = tk.Button(
            sidebar,
            text="  ▶  RUN ALGORITHM  ",
            font=("Courier", 11, "bold"),
            fg=COLORS["bg"],
            bg=COLORS["accent"],
            activebackground=COLORS["accent2"],
            activeforeground=COLORS["text"],
            relief="flat",
            cursor="hand2",
            command=self._run_algorithm,
            pady=10
        )
        run_btn.pack(fill="x", padx=18, pady=6)

        # Compare All button
        cmp_btn = tk.Button(
            sidebar,
            text="  ⊞  COMPARE ALL  ",
            font=("Courier", 10, "bold"),
            fg=COLORS["accent2"],
            bg=COLORS["card"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="flat",
            cursor="hand2",
            command=self._run_comparison,
            pady=8
        )
        cmp_btn.pack(fill="x", padx=18, pady=4)

        # Reset
        rst_btn = tk.Button(
            sidebar,
            text="  ↺  RESET  ",
            font=("Courier", 9),
            fg=COLORS["text_dim"],
            bg=COLORS["panel"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text_mid"],
            relief="flat",
            cursor="hand2",
            command=self._reset,
            pady=6
        )
        rst_btn.pack(fill="x", padx=18, pady=4)

        # Toggle Theme
        theme_btn = tk.Button(
            sidebar,
            text="  ◑  TOGGLE THEME  ",
            font=("Courier", 9),
            fg=COLORS["text_dim"],
            bg=COLORS["panel"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text_mid"],
            relief="flat",
            cursor="hand2",
            command=self._toggle_theme,
            pady=6
        )
        theme_btn.pack(fill="x", padx=18, pady=4)

        tk.Frame(sidebar, bg=COLORS["bg"], height=12).pack(fill="x")
        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=0)
        tk.Frame(sidebar, bg=COLORS["bg"], height=12).pack(fill="x")

        # Legend
        self._section_label(sidebar, "LEGEND")
        legend_items = [
            (COLORS["accent"],  "Default Node"),
            (COLORS["green"],   "Visited Node"),
            (COLORS["gold"],    "Optimal Path"),
            (COLORS["red"],     "Start / Goal"),
            (COLORS["edge_active"], "Active Edge"),
        ]
        for color, label in legend_items:
            row = tk.Frame(sidebar, bg=COLORS["panel"])
            row.pack(fill="x", padx=18, pady=3)
            tk.Canvas(row, width=14, height=14, bg=COLORS["panel"],
                      highlightthickness=0).pack(side="left")
            c = tk.Canvas(row, width=14, height=14, bg=COLORS["panel"],
                          highlightthickness=0)
            c.pack(side="left")
            c.create_oval(2, 2, 12, 12, fill=color, outline="")
            tk.Label(row, text=label,
                     font=("Courier", 9),
                     fg=COLORS["text_mid"], bg=COLORS["panel"]).pack(side="left", padx=6)

    def _section_label(self, parent, text):
        tk.Frame(parent, bg=COLORS["bg"], height=14).pack(fill="x")
        tk.Label(parent, text=text,
                 font=("Courier", 8, "bold"),
                 fg=COLORS["accent"], bg=COLORS["panel"],
                 anchor="w").pack(fill="x", padx=18)
        tk.Frame(parent, bg=COLORS["bg"], height=4).pack(fill="x")

    def _node_dropdown(self, parent, var):
        node_list = [f"{nid} – {self.graph.node_name(nid)}"
                     for nid in sorted(self.graph.nodes)]
        om = ttk.Combobox(parent, textvariable=var,
                          values=[nid for nid in sorted(self.graph.nodes)],
                          font=("Courier", 11),
                          state="readonly", width=18)
        om.pack(padx=18, pady=4, fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox",
                        fieldbackground=COLORS["card"],
                        background=COLORS["card"],
                        foreground=COLORS["text"],
                        selectbackground=COLORS["card"],
                        selectforeground=COLORS["accent"],
                        arrowcolor=COLORS["accent"])

    def _radio_btn(self, parent, text, value):
        rb = tk.Radiobutton(
            parent, text=text,
            variable=self.algo_var, value=value,
            font=("Courier", 10),
            fg=COLORS["text_mid"], bg=COLORS["panel"],
            selectcolor=COLORS["card"],
            activebackground=COLORS["panel"],
            activeforeground=COLORS["accent"],
            cursor="hand2",
            indicatoron=True
        )
        rb.pack(anchor="w", padx=20, pady=2)

    def _build_canvas(self, parent):
        # Title above canvas
        info_bar = tk.Frame(parent, bg=COLORS["bg"], height=36)
        info_bar.pack(fill="x")
        info_bar.pack_propagate(False)

        self.status_label = tk.Label(
            info_bar,
            text="Select source & destination, then run an algorithm.",
            font=("Courier", 10),
            fg=COLORS["text_mid"], bg=COLORS["bg"]
        )
        self.status_label.pack(side="left", padx=20, pady=8)

        # Canvas with border
        canvas_container = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        canvas_container.pack(padx=16, pady=(0, 16))

        self.canvas = tk.Canvas(
            canvas_container,
            width=CANVAS_W, height=CANVAS_H,
            bg=COLORS["bg"],
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack()
        self.canvas.bind("<Motion>", self._on_canvas_hover)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _build_right_panel(self, parent):
        panel = tk.Frame(parent, bg=COLORS["panel"], width=280)
        panel.pack(side="right", fill="y")
        panel.pack_propagate(False)

        tk.Frame(panel, bg=COLORS["border"], height=1).pack(fill="x")

        self._section_label(panel, "TRAVERSAL LOG")

        # Log text area
        log_frame = tk.Frame(panel, bg=COLORS["card"],
                             highlightbackground=COLORS["border"],
                             highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        self.log_text = tk.Text(
            log_frame,
            font=("Courier", 9),
            fg=COLORS["text_mid"], bg=COLORS["card"],
            insertbackground=COLORS["accent"],
            relief="flat", wrap="word",
            padx=10, pady=10,
            state="disabled"
        )
        scrollbar = tk.Scrollbar(log_frame, bg=COLORS["card"],
                                 troughcolor=COLORS["bg"],
                                 command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # Tag colors
        self.log_text.tag_config("accent",  foreground=COLORS["accent"])
        self.log_text.tag_config("gold",    foreground=COLORS["gold"])
        self.log_text.tag_config("green",   foreground=COLORS["green"])
        self.log_text.tag_config("dim",     foreground=COLORS["text_dim"])
        self.log_text.tag_config("header",  foreground=COLORS["accent2"])

        # Stats cards
        self._section_label(panel, "STATISTICS")
        self.stats_frame = tk.Frame(panel, bg=COLORS["panel"])
        self.stats_frame.pack(fill="x", padx=14, pady=(0, 14))
        self._build_stat_cards()

    def _build_stat_cards(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = [
            ("PATH COST",       "—",  COLORS["gold"]),
            ("NODES EXPLORED",  "—",  COLORS["green"]),
            ("PATH LENGTH",     "—",  COLORS["accent"]),
        ]
        self.stat_labels = {}
        for title, val, color in stats:
            card = tk.Frame(self.stats_frame, bg=COLORS["card"],
                            highlightbackground=COLORS["border"],
                            highlightthickness=1)
            card.pack(fill="x", pady=4)

            tk.Label(card, text=title,
                     font=("Courier", 7, "bold"),
                     fg=COLORS["text_dim"], bg=COLORS["card"],
                     anchor="w").pack(fill="x", padx=10, pady=(8, 0))

            lbl = tk.Label(card, text=val,
                           font=("Courier", 18, "bold"),
                           fg=color, bg=COLORS["card"],
                           anchor="w")
            lbl.pack(fill="x", padx=10, pady=(0, 8))
            self.stat_labels[title] = lbl

    # ── Graph Drawing ─────────────────────────────────────────────────────────

    def _draw_graph(self, result=None, highlight_nodes=None, highlight_path=None):
        self.canvas.delete("all")
        self._draw_grid()

        path_set = set(highlight_path or [])
        visited_set = set(highlight_nodes or [])
        path_edges = set()
        if highlight_path and len(highlight_path) > 1:
            for i in range(len(highlight_path) - 1):
                path_edges.add((highlight_path[i], highlight_path[i+1]))
                path_edges.add((highlight_path[i+1], highlight_path[i]))

        # Draw edges first
        drawn_edges = set()
        for u in self.graph.nodes:
            for v, w in self.graph.get_neighbors(u):
                if (v, u) in drawn_edges:
                    continue
                drawn_edges.add((u, v))
                self._draw_edge(u, v, w, (u, v) in path_edges or (v, u) in path_edges)

        # Draw nodes
        for node_id in self.graph.nodes:
            is_start  = (node_id == self.start_node)
            is_goal   = (node_id == self.goal_node)
            is_path   = node_id in path_set
            is_visited = node_id in visited_set
            is_hover  = node_id == self.hover_node
            self._draw_node(node_id, is_start, is_goal, is_path, is_visited, is_hover)

    def _draw_grid(self):
        """Subtle dot grid background."""
        for x in range(0, CANVAS_W, 40):
            for y in range(0, CANVAS_H, 40):
                self.canvas.create_oval(x-1, y-1, x+1, y+1,
                                        fill=COLORS["border"], outline="")

    def _draw_edge(self, u, v, weight, is_active):
        x1, y1 = self.graph.get_position(u)
        x2, y2 = self.graph.get_position(v)

        if is_active:
            # Glow effect: multiple lines with decreasing width
            self.canvas.create_line(x1, y1, x2, y2,
                                    fill=COLORS["gold"], width=6, capstyle="round")
            self.canvas.create_line(x1, y1, x2, y2,
                                    fill=COLORS["edge_glow"], width=2, capstyle="round")
        else:
            self.canvas.create_line(x1, y1, x2, y2,
                                    fill=COLORS["edge"], width=1.5, capstyle="round",
                                    dash=(4, 4))

        # Weight label
        mx, my = (x1+x2)//2, (y1+y2)//2
        self.canvas.create_text(mx, my - 6, text=str(weight),
                                font=("Courier", 8),
                                fill=COLORS["gold"] if is_active else COLORS["text_dim"])

    def _draw_node(self, node_id, is_start, is_goal, is_path, is_visited, is_hover):
        x, y = self.graph.get_position(node_id)
        r = NODE_RADIUS + (4 if is_hover else 0)

        # Determine colors
        if is_start or is_goal:
            fill    = COLORS["goal_fill"] if is_goal else COLORS["start_fill"]
            outline = COLORS["red"]
            lcolor  = COLORS["red"]
            glow    = COLORS["red"]
        elif is_path:
            fill    = COLORS["path_fill"]
            outline = COLORS["gold"]
            lcolor  = COLORS["gold"]
            glow    = COLORS["gold"]
        elif is_visited:
            fill    = COLORS["visited_fill"]
            outline = COLORS["green"]
            lcolor  = COLORS["green"]
            glow    = COLORS["green"]
        else:
            fill    = COLORS["node_default"]
            outline = COLORS["accent"] if is_hover else COLORS["node_border"]
            lcolor  = COLORS["accent"] if is_hover else COLORS["text_mid"]
            glow    = COLORS["accent"]

        # Glow ring (larger, semi-transparent look via layering)
        if is_path or is_start or is_goal or is_visited or is_hover:
            self.canvas.create_oval(x-r-6, y-r-6, x+r+6, y+r+6,
                                    fill="", outline=glow, width=1)

        # Main circle
        self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                fill=fill, outline=outline, width=2)

        # Node ID
        self.canvas.create_text(x, y-5, text=node_id,
                                font=("Courier", 11, "bold"),
                                fill=lcolor)

        # City name (short)
        name = self.graph.node_name(node_id)
        short = name[:8] + "…" if len(name) > 8 else name
        self.canvas.create_text(x, y+9, text=short,
                                font=("Courier", 7),
                                fill=COLORS["text_dim"])

    # ── Interaction ───────────────────────────────────────────────────────────

    def _find_node_at(self, cx, cy):
        """Return node_id if click/hover is within a node circle."""
        for node_id in self.graph.nodes:
            x, y = self.graph.get_position(node_id)
            if math.sqrt((cx-x)**2 + (cy-y)**2) <= NODE_RADIUS + 6:
                return node_id
        return None

    def _on_canvas_hover(self, event):
        node = self._find_node_at(event.x, event.y)
        if node != self.hover_node:
            self.hover_node = node
            self._redraw_current()

    def _on_canvas_click(self, event):
        node = self._find_node_at(event.x, event.y)
        if not node:
            return
        if not self.start_node:
            self.start_node = node
            self.src_var.set(node)
            self.status_label.config(text=f"Start: {self.graph.node_name(node)}  — Now click a destination.")
        elif not self.goal_node and node != self.start_node:
            self.goal_node = node
            self.dst_var.set(node)
            self.status_label.config(text=f"Route: {self.graph.node_name(self.start_node)} → {self.graph.node_name(node)}")
        else:
            self.start_node = node
            self.goal_node  = None
            self.src_var.set(node)
            self.status_label.config(text=f"Start reset to {self.graph.node_name(node)}")
        self._redraw_current()

    def _redraw_current(self):
        if self.result:
            self._draw_graph(
                result=self.result,
                highlight_nodes=self.result["visited_order"],
                highlight_path=self.result["path"]
            )
        else:
            self._draw_graph()

    # ── Algorithm Execution ───────────────────────────────────────────────────

    def _run_algorithm(self):
        from algorithms import dijkstra, astar, greedy_best_first

        src = self.src_var.get()
        dst = self.dst_var.get()
        algo = self.algo_var.get()

        if src == dst:
            self._set_log(["⚠ Source and destination must be different."])
            return

        self.start_node = src
        self.goal_node  = dst

        algo_map = {
            "dijkstra": ("Dijkstra's Algorithm", dijkstra, COLORS["accent"]),
            "astar":    ("A* Search",            astar,    COLORS["accent2"]),
            "greedy":   ("Greedy Best-First",     greedy_best_first, COLORS["gold"]),
        }
        name, fn, color = algo_map[algo]

        self.result = fn(self.graph, src, dst)
        path = self.result["path"]
        cost = self.result["cost"]

        # Update status
        if path:
            route_str = " → ".join(self.graph.node_name(n) for n in path)
            self.status_label.config(
                text=f"[{name}]  {self.graph.node_name(src)} → {self.graph.node_name(dst)}   Cost: {cost:.1f} km",
                fg=color
            )
        else:
            self.status_label.config(text="No path found.", fg=COLORS["red"])

        # Update log
        self._set_log(self.result["log"], algo)

        # Update stat cards
        self.stat_labels["PATH COST"].config(
            text=f"{cost:.1f} km" if cost >= 0 else "N/A")
        self.stat_labels["NODES EXPLORED"].config(
            text=str(self.result["nodes_explored"]))
        self.stat_labels["PATH LENGTH"].config(
            text=f"{len(path)} nodes" if path else "N/A")

        self._draw_graph(
            result=self.result,
            highlight_nodes=self.result["visited_order"],
            highlight_path=path
        )

    def _run_comparison(self):
        from algorithms import dijkstra, astar, greedy_best_first

        src = self.src_var.get()
        dst = self.dst_var.get()

        if src == dst:
            self._set_log(["⚠ Source and destination must be different."])
            return

        self.start_node = src
        self.goal_node  = dst

        results = {
            "Dijkstra": dijkstra(self.graph, src, dst),
            "A*":       astar(self.graph, src, dst),
            "Greedy":   greedy_best_first(self.graph, src, dst),
        }

        lines = [
            "╔══════════════════════════════════════╗",
            "║        ALGORITHM COMPARISON          ║",
            "╚══════════════════════════════════════╝",
            f"  Route: {self.graph.node_name(src)} → {self.graph.node_name(dst)}",
            "",
        ]
        best_algo = min(results, key=lambda a: results[a]["cost"] if results[a]["cost"] >= 0 else 1e9)

        for algo_name, res in results.items():
            cost = res["cost"]
            nodes = res["nodes_explored"]
            plen  = len(res["path"])
            mark  = " ← BEST COST" if algo_name == best_algo else ""
            lines += [
                f"── {algo_name} ──",
                f"  Cost       : {cost:.1f} km{mark}",
                f"  Nodes Expl : {nodes}",
                f"  Path Len   : {plen} nodes",
                f"  Path       : {' → '.join(self.graph.node_name(n) for n in res['path'])}",
                "",
            ]

        self._set_log(lines, "comparison")
        self.status_label.config(
            text=f"Comparison complete — Best cost: {best_algo}  ({results[best_algo]['cost']:.1f} km)",
            fg=COLORS["gold"]
        )

        # Highlight the best result on canvas
        self.result = results[best_algo]
        self._draw_graph(
            result=self.result,
            highlight_nodes=self.result["visited_order"],
            highlight_path=self.result["path"]
        )

        # Update stats
        best = results[best_algo]
        self.stat_labels["PATH COST"].config(text=f"{best['cost']:.1f} km")
        self.stat_labels["NODES EXPLORED"].config(text=str(best["nodes_explored"]))
        self.stat_labels["PATH LENGTH"].config(text=f"{len(best['path'])} nodes")

    def _reset(self):
        self.start_node = None
        self.goal_node  = None
        self.result     = None
        self.status_label.config(
            text="Select source & destination, then run an algorithm.",
            fg=COLORS["text_mid"]
        )
        self._set_log(["Graph reset. Select nodes and run an algorithm."])
        self._build_stat_cards()
        self._draw_graph()

    def _toggle_theme(self):
        # Save state
        old_src = self.src_var.get()
        old_dst = self.dst_var.get()
        old_algo = self.algo_var.get()
        status_text = self.status_label.cget("text")
        
        # Toggle colors
        self.is_dark_mode = not self.is_dark_mode
        COLORS.update(DARK_COLORS if self.is_dark_mode else LIGHT_COLORS)
        
        # Rebuild UI
        self.root.configure(bg=COLORS["bg"])
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self._build_ui()
        
        # Restore state
        self.src_var.set(old_src)
        self.dst_var.set(old_dst)
        self.algo_var.set(old_algo)
        
        if self.result:
            self.status_label.config(text=status_text, fg=COLORS["gold"])
        else:
            self.status_label.config(text=status_text, fg=COLORS["text_mid"])
            
        if self.log_history:
            self._set_log(self.log_history)
            
        if self.result:
            if "cost" in self.result:
                best = self.result
                self.stat_labels["PATH COST"].config(text=f"{best['cost']:.1f} km" if best['cost'] >= 0 else "N/A")
                self.stat_labels["NODES EXPLORED"].config(text=str(best["nodes_explored"]))
                self.stat_labels["PATH LENGTH"].config(text=f"{len(best['path'])} nodes" if best['path'] else "N/A")
                
        self._draw_graph(
            result=self.result,
            highlight_nodes=self.result["visited_order"] if self.result else None,
            highlight_path=self.result["path"] if self.result else None
        )

    # ── Log Helper ────────────────────────────────────────────────────────────

    def _set_log(self, lines, algo=None):
        self.log_history = lines
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        for line in lines:
            if line.startswith("▶") or line.startswith("╔") or line.startswith("╚"):
                self.log_text.insert("end", line + "\n", "header")
            elif line.startswith("✔") or "BEST" in line:
                self.log_text.insert("end", line + "\n", "gold")
            elif line.startswith("  POP"):
                self.log_text.insert("end", line + "\n", "accent")
            elif "↳" in line:
                self.log_text.insert("end", line + "\n", "green")
            elif line.startswith("PATH") or line.startswith("COST"):
                self.log_text.insert("end", line + "\n", "gold")
            elif line.startswith("─") or line.startswith("══"):
                self.log_text.insert("end", line + "\n", "dim")
            else:
                self.log_text.insert("end", line + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see("end")

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
