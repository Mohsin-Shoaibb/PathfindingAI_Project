
MAX_DEPTH = 200   # safety ceiling so we never loop forever


def _reconstruct(came_from: dict, start: tuple, goal: tuple) -> list[tuple]:
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    if path and path[0] == start:
        return path
    return []


def _dls_inner(grid, start, goal, limit):
    """
    Single DLS pass used internally by IDDFS.
    Yields (frontier, explored, came_from, found) frames.
    """
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

        yield frozenset(frontier), frozenset(explored), came_from, False

        if current == goal:
            yield frozenset(frontier), frozenset(explored), came_from, True
            return

        if depth < limit:
            r, c = current
            node = grid.node(r, c)
            for nb in grid.neighbours(node):
                if nb.pos not in explored:
                    # FIX: always overwrite came_from so the recorded parent
                    # matches the branch that will actually be expanded (LIFO).
                    came_from[nb.pos] = current
                    stack.append((nb.pos, depth + 1))
                    frontier.add(nb.pos)


def iddfs(grid):
    """
    Iterative Deepening DFS generator.

    Parameters
    ----------
    grid : Grid   Shared grid object.

    Yields
    ------
    dict  Algorithm state snapshot.
    """
    start = grid.start_node.pos
    goal  = grid.target_node.pos

    last_explored = frozenset()   # initialised here so the exhaustion
                                  # yield is always safe (Bug 6 fix)

    for limit in range(0, MAX_DEPTH + 1):
        last_frontier = frozenset()

        for frontier, explored, came_from, goal_hit in \
                _dls_inner(grid, start, goal, limit):

            last_frontier = frontier
            last_explored = explored

            yield {
                "frontier"   : frontier,
                "explored"   : explored,
                "path"       : None,
                "done"       : False,
                "found"      : False,
                "iteration"  : limit,
                "depth_limit": limit,
            }

            if goal_hit:
                path = _reconstruct(came_from, start, goal)
                yield {
                    "frontier"   : frontier,
                    "explored"   : explored,
                    "path"       : path,
                    "done"       : True,
                    "found"      : True,
                    "iteration"  : limit,
                    "depth_limit": limit,
                }
                return

    # Exhausted all depth levels — no path exists within MAX_DEPTH
    yield {
        "frontier"   : frozenset(),
        "explored"   : last_explored,
        "path"       : [],
        "done"       : True,
        "found"      : False,
        "iteration"  : MAX_DEPTH,
        "depth_limit": MAX_DEPTH,
    }