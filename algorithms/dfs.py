
# Cells with weight strictly greater than this are skipped by DFS
DFS_WEIGHT_LIMIT = 7


def _reconstruct(came_from: dict, start: tuple, goal: tuple) -> list[tuple]:
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    if path and path[0] == start:
        return path
    return []


def dfs(grid, weight_limit: int = DFS_WEIGHT_LIMIT):
    """
    Depth-First Search generator.

    Parameters
    ----------
    grid         : Grid   Shared grid object.
    weight_limit : int    Cells with weight > this value are ignored.

    Yields
    ------
    dict  Algorithm state snapshot.
    """
    start = grid.start_node.pos
    goal  = grid.target_node.pos

    stack     = [start]
    came_from = {start: None}
    explored  = set()
    frontier  = {start}

    while stack:
        current = stack.pop()
        frontier.discard(current)

        if current in explored:
            continue
        explored.add(current)

        # ── Yield frame ────────────────────────────────────────────────
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

        # ── Expand: skip high-weight ("negative") cells ────────────────
        r, c = current
        node = grid.node(r, c)
        for nb in grid.neighbours(node):
            if nb.pos not in explored:
                # FIX 2: exempt the target from the weight filter so a
                # high-weight target node is never silently skipped.
                if nb.weight > weight_limit and nb.pos != goal:
                    continue
                # FIX 1: always overwrite came_from so the recorded parent
                # matches the branch that will actually be expanded (LIFO).
                came_from[nb.pos] = current
                stack.append(nb.pos)
                frontier.add(nb.pos)

    # ── No path found ──────────────────────────────────────────────────
    yield {
        "frontier" : frozenset(),
        "explored" : frozenset(explored),
        "path"     : [],
        "done"     : True,
        "found"    : False,
    }