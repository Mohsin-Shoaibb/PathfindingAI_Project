# 🔍 OG Path Hunter

A interactive pathfinding algorithm visualizer built with Python and Pygame. Draw walls, place start/target nodes, and watch six classic search algorithms explore your maze in real time.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python) ![Pygame](https://img.shields.io/badge/Pygame-2.x-green?logo=pygame)
---

## ✨ Features

- **6 search algorithms** selectable from a sidebar UI
- **Animated step-by-step** exploration with adjustable speed
- **Interactive grid editor** — click and drag to draw/erase walls
- **Weighted cells** — UCS responds to traversal costs (weight 1–10)
- **Dual frontier visualization** for Bidirectional BFS
- **Pulsing color animations** for frontier cells
- **Scrollable sidebar** with color legend, sliders, and algorithm info
- **Keyboard shortcuts** for fast control

---

## 🧠 Algorithms

| Key | Algorithm | Optimal? | Notes |
|-----|-----------|----------|-------|
| **BFS** | Breadth-First Search | ✅ (unweighted) | Explores layer by layer; guaranteed shortest path on uniform grids |
| **DFS** | Depth-First Search | ❌ | Fast but non-optimal; skips cells with weight > 7 |
| **UCS** | Uniform-Cost Search | ✅ | Dijkstra-style; finds cheapest path on weighted grids |
| **DLS** | Depth-Limited Search | ❌ | DFS with a configurable depth ceiling (slider, default 15) |
| **IDDFS** | Iterative Deepening DFS | ✅ (unweighted) | Re-runs DLS at increasing depths; combines DFS memory with BFS optimality |
| **BIDIR** | Bidirectional BFS | ✅ (unweighted) | Simultaneous forward + backward search; meets in the middle |

---

## 🗂 Project Structure

```
og-path-hunter/
├── main.py          # Pygame app, UI layout, event loop
├── grid.py          # Grid and Node classes, neighbour expansion
├── node.py          # Node cell with state, weight, wall logic
└── algorithms/
    ├── bfs.py       # Breadth-First Search
    ├── dfs.py       # Depth-First Search
    ├── ucs.py       # Uniform-Cost Search
    ├── dls.py       # Depth-Limited Search
    ├── iddfs.py     # Iterative Deepening DFS
    └── bidirectional.py  # Bidirectional BFS
```

> Each algorithm is a **Python generator** that yields state snapshots (`frontier`, `explored`, `path`, `done`, `found`). The GUI consumes one snapshot per animation frame, keeping algorithms fully decoupled from rendering.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Pygame 2.x

### Installation

```bash
# Clone the repository
git clone https://github.com/mohsin-shoaibb/PathfindingAI_Project.git
cd og-path-hunter

# Install dependencies
pip install pygame
```

### Run

```bash
python main.py
```

---

## 🎮 Controls

### Keyboard

| Key | Action |
|-----|--------|
| `Space` | Start search |
| `R` | Reset grid |
| `Esc` | Deselect current edit tool |
| `↑` / `↓` | Scroll sidebar |

### Mouse

| Action | Effect |
|--------|--------|
| Click algorithm button | Select algorithm |
| Click **Set Start** → click cell | Place start node |
| Click **Set Target** → click cell | Place target node |
| Click **Draw Walls** → click/drag | Paint walls |
| Click **Erase Walls** → click/drag | Erase walls |
| Scroll wheel (over sidebar) | Scroll sidebar |

---

## 🖥 UI Overview

```
┌────────────────┬──────────────────────────────────────┐
│   SIDEBAR      │  TOP BAR  (title / status / stats)   │
│                ├──────────────────────────────────────┤
│  Algorithm     │                                      │
│  selector      │                                      │
│                │           GRID                       │
│  Edit tools    │      (20 × 30 cells)                 │
│                │                                      │
│  DLS slider    │                                      │
│  Speed slider  │                                      │
│                │                                      │
│  ▶ START       │                                      │
│  ⟳ RESET ALL  │                                      │
│                │                                      │
│  Color legend  │                                      │
└────────────────┴──────────────────────────────────────┘
```

### Cell Colors

| Color | Meaning |
|-------|---------|
| 🟢 Green | Start node |
| 🔴 Red | Target node |
| ⬛ Dark | Wall |
| 🔵 Blue (pulsing) | Frontier (forward) |
| 💙 Light blue (pulsing) | Frontier (backward — Bidirectional only) |
| 🟦 Dark blue | Explored |
| 🟡 Yellow | Final path |

---

## ⚙️ Configuration

Key constants at the top of `main.py` let you resize the window and grid without touching any other code:

```python
GRID_ROWS  = 20    # number of grid rows
GRID_COLS  = 30    # number of grid columns
CELL_SIZE  = 30    # pixels per cell
SIDEBAR_W  = 340   # sidebar width in pixels
```

---

## 🔌 Adding a New Algorithm

1. Create a generator function in `algorithms/` that yields snapshots:

```python
def my_algo(grid):
    # ... your search logic ...
    yield {
        "frontier": frozenset(...),
        "explored": frozenset(...),
        "path":     None,          # or list of (row, col) tuples when found
        "done":     False,
        "found":    False,
    }
```

2. Import it in `main.py` and add one line to `ALGO_LIST`:

```python
ALGO_LIST = [
    ...
    ("MINE", "My Algorithm", my_algo),
]
```

That's it — the button, UI state, and rendering are all handled automatically.

---

## 📐 Grid Connectivity

The grid uses **6-directional movement** (not the standard 4 or 8):

```
  ↖  ↑
← ·  →
  ↓  ↘
```

Specifically: Up, Right, Down, Bottom-Right (diagonal), Left, Top-Left (diagonal). Top-Right and Bottom-Left diagonals are excluded by design.

---
