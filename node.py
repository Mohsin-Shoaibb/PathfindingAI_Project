class Node:
    """Single cell in the pathfinding grid."""

    # state can be: 'empty', 'wall', 'start', 'target',
    #               'frontier', 'frontier2', 'explored', 'path', 'dynamic'
    __slots__ = ("row", "col", "weight", "is_wall", "is_dynamic", "state")

    def __init__(self, row: int, col: int, weight: int = 1):
        self.row        = row
        self.col        = col
        self.weight     = weight    # 1 = free, 2–10 = increasing traversal cost
        self.is_wall    = False
        self.is_dynamic = False
        self.state      = "empty"

    # These let Node sit inside a heapq without Python trying to compare objects directly
    def __lt__(self, other: "Node") -> bool:
        return (self.row, self.col) < (other.row, other.col)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __repr__(self) -> str:
        return f"Node({self.row},{self.col}, w={self.weight}, {self.state})"

    @property
    def pos(self) -> tuple:
        # (row, col) used as dict/set keys throughout the algorithms
        return (self.row, self.col)

    @property
    def blocked(self) -> bool:
        # True for both static walls and runtime dynamic obstacles
        return self.is_wall or self.is_dynamic

    def reset_search_state(self):
        # Called between runs — clears visual state but keeps wall and weight
        self.is_dynamic = False
        if not self.is_wall:
            self.state = "empty"

    def mark_wall(self, flag: bool = True):
        self.is_wall = flag
        self.state   = "wall" if flag else "empty"

    def mark_dynamic(self):
        self.is_dynamic = True
        self.state      = "dynamic"

    # The three mark_* methods below guard against overwriting endpoint / wall states
    def mark_frontier(self):
        if self.state not in ("start", "target", "wall", "dynamic"):
            self.state = "frontier"

    def mark_explored(self):
        if self.state not in ("start", "target", "wall", "dynamic"):
            self.state = "explored"

    def mark_path(self):
        if self.state not in ("start", "target", "wall", "dynamic"):
            self.state = "path"