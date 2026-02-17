
from collections import deque


def _reconstruct(came_from: dict, start: tuple, goal: tuple) -> list[tuple]:
    """Trace parent pointers from goal back to start."""
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    # Verify the path actually reaches start (safety check)
    if path and path[0] == start:
        return path
    return []


def bfs(grid):
    """
    Breadth-First Search generator.

    Parameters
    ----------
    grid : Grid   The shared grid object (from grid.py)

    Yields
    ------
    dict  Snapshot of algorithm state (see module docstring).
    """
    start = grid.start_node.pos
    goal  = grid.target_node.pos

    queue     = deque([start])
    came_from = {start: None}     # tracks parents for path reconstruction
    explored  = set()
    frontier  = {start}           # everything currently in the queue

    while queue:
        current = queue.popleft()
        frontier.discard(current)
        explored.add(current)

        # ── Yield current state so GUI draws this frame ────────────────
        yield {
            "frontier" : frozenset(frontier),
            "explored" : frozenset(explored),
            "path"     : None,
            "done"     : False,
            "found"    : False,
        }

        # ── Goal test ──────────────────────────────────────────────────
        if current == goal:
            path = _reconstruct(came_from, start, goal)
            yield {
                "frontier" : frozenset(frontier),
                "explored" : frozenset(explored),
                "path"     : path,
                "done"     : True,
                "found"    : True,
            }
            return

        # ── Expand neighbours ──────────────────────────────────────────
        r, c = current
        node = grid.node(r, c)
        for nb in grid.neighbours(node):
            nb_pos = nb.pos
            if nb_pos not in came_from:
                came_from[nb_pos] = current
                queue.append(nb_pos)
                frontier.add(nb_pos)

    # ── Queue exhausted — no path ──────────────────────────────────────
    yield {
        "frontier" : frozenset(),
        "explored" : frozenset(explored),
        "path"     : [],
        "done"     : True,
        "found"    : False,
    }