from node import Node
# 6-directional clockwise movement: Up, Right, Down, Bottom-Right, Left, Top-Left.
# Top-Right (-1,+1) and Bottom-Left (+1,-1) are excluded per spec.
DIRECTIONS = [
    (-1,  0),   # Up
    ( 0,  1),   # Right
    ( 1,  0),   # Down
    ( 1,  1),   # Bottom-Right (main diagonal)
    ( 0, -1),   # Left
    (-1, -1),   # Top-Left     (main diagonal)
]


class Grid:
    """2-D grid of Node objects used by all search algorithms."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self._cells: list[list[Node]] = [
            [Node(r, c) for c in range(cols)] for r in range(rows)
        ]
        self.start_node:  Node | None = None
        self.target_node: Node | None = None

        self._set_default_endpoints()

    # ── Internal helpers 

    def _set_default_endpoints(self):
        # Start on the left side, target on the right, both on the middle row
        mid_r = self.rows // 2
        self.set_start(mid_r, 3)
        self.set_target(mid_r, self.cols - 4)

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    # ── Public accessors 

    def node(self, r: int, c: int) -> Node:
        return self._cells[r][c]

    def all_nodes(self):
        """Iterate every node left-to-right, top-to-bottom."""
        for row in self._cells:
            yield from row

    # ── Endpoint setters 

    def set_start(self, r: int, c: int):
        # Clear the old start cell before moving it
        if self.start_node:
            self.start_node.state = "empty"
        self.start_node = self._cells[r][c]
        self.start_node.state = "start"
        self.start_node.is_wall = False
        self.start_node.is_dynamic = False

    def set_target(self, r: int, c: int):
        if self.target_node:
            self.target_node.state = "empty"
        self.target_node = self._cells[r][c]
        self.target_node.state = "target"
        self.target_node.is_wall = False
        self.target_node.is_dynamic = False

    # ── Wall management 

    def toggle_wall(self, r: int, c: int):
        nd = self._cells[r][c]
        if nd is self.start_node or nd is self.target_node:
            return  # never wall over an endpoint
        nd.mark_wall(not nd.is_wall)

    def place_wall(self, r: int, c: int):
        nd = self._cells[r][c]
        if nd is self.start_node or nd is self.target_node:
            return
        nd.mark_wall(True)

    def erase_wall(self, r: int, c: int):
        self._cells[r][c].mark_wall(False)

    # ── Weight management 

    def set_weight(self, r: int, c: int, w: int):
        """Set traversal cost (1–10). Walls and endpoints are unaffected."""
        nd = self._cells[r][c]
        if nd.is_wall or nd is self.start_node or nd is self.target_node:
            return
        nd.weight = max(1, min(10, w))

    # ── Neighbour expansion 

    def neighbours(self, node: Node) -> list[Node]:
        """Return walkable neighbours in the clockwise order defined by DIRECTIONS."""
        result = []
        for dr, dc in DIRECTIONS:
            nr, nc = node.row + dr, node.col + dc
            if not self._in_bounds(nr, nc):
                continue
            nb = self._cells[nr][nc]
            if not nb.blocked:
                result.append(nb)
        return result

    def neighbours_pos(self, pos: tuple) -> list[tuple]:
        """Same as neighbours() but returns (row, col) tuples instead of Node objects."""
        r, c = pos
        result = []
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if not self._in_bounds(nr, nc):
                continue
            nb = self._cells[nr][nc]
            if not nb.blocked:
                result.append((nr, nc))
        return result

    # ── Reset 

    def reset_search(self):
        """Clear frontier / explored / path state. Walls and weights are preserved."""
        for nd in self.all_nodes():
            nd.reset_search_state()
        # reset_search_state wipes the state string, so re-apply endpoint colours
        if self.start_node:
            self.start_node.state = "start"
        if self.target_node:
            self.target_node.state = "target"

    def full_reset(self):
        """Wipe everything — walls, weights, endpoints — back to a blank grid."""
        for nd in self.all_nodes():
            nd.is_wall    = False
            nd.is_dynamic = False
            nd.weight     = 1
            nd.state      = "empty"
        self.start_node  = None
        self.target_node = None
        self._set_default_endpoints()

    def __repr__(self) -> str:
        return f"Grid({self.rows}×{self.cols})"