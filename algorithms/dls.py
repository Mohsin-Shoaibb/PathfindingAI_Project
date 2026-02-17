
DEFAULT_DEPTH_LIMIT = 15


def _reconstruct(came_from: dict, start: tuple, goal: tuple) -> list[tuple]:
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    if path and path[0] == start:
        return path
    return []


def dls(grid, depth_limit: int = DEFAULT_DEPTH_LIMIT):
    """
    Depth-Limited Search generator.

    Uses an explicit stack of (position, depth) to avoid Python
    recursion limits on large grids.

    Parameters
    ----------
    grid        : Grid  Shared grid object.
    depth_limit : int   Maximum search depth (default 15).

    Yields
    ------
    dict  Algorithm state snapshot including 'depth_limit' key.
    """
    start = grid.start_node.pos
    goal  = grid.target_node.pos

    # Stack entries: (position, current_depth)
    stack     = [(start, 0)]
    came_from = {start: None}
    explored  = set()
    frontier  = {start}

    while stack:
        current, depth = stack.pop()
        frontier.discard(current)

        if current in explored:
            continue
        explored.add(current)

        # ── Yield frame ────────────────────────────────────────────────
        yield {
            "frontier"     : frozenset(frontier),
            "explored"     : frozenset(explored),
            "path"         : None,
            "done"         : False,
            "found"        : False,
            "depth_limit"  : depth_limit,
            "current_depth": depth,
        }

        # ── Goal test ──────────────────────────────────────────────────
        if current == goal:
            path = _reconstruct(came_from, start, goal)
            yield {
                "frontier"     : frozenset(frontier),
                "explored"     : frozenset(explored),
                "path"         : path,
                "done"         : True,
                "found"        : True,
                "depth_limit"  : depth_limit,
                "current_depth": depth,
            }
            return

        # ── Only expand if within depth limit ──────────────────────────
        if depth < depth_limit:
            r, c = current
            node = grid.node(r, c)
            for nb in grid.neighbours(node):
                if nb.pos not in explored:
                    # FIX: always overwrite came_from so the recorded parent
                    # matches the branch that will actually be expanded (LIFO).
                    came_from[nb.pos] = current
                    stack.append((nb.pos, depth + 1))
                    frontier.add(nb.pos)

    # ── No path within depth limit ─────────────────────────────────────
    yield {
        "frontier"     : frozenset(),
        "explored"     : frozenset(explored),
        "path"         : [],
        "done"         : True,
        "found"        : False,
        "depth_limit"  : depth_limit,
        "current_depth": depth_limit,
    }