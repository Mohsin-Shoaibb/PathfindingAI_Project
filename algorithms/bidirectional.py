
from collections import deque


def _trace(came_from: dict, start: tuple, end: tuple) -> list[tuple]:
    """Reconstruct a one-directional path using came_from pointers."""
    path, node = [], end
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    if path and path[0] == start:
        return path
    return []


def _build_path(fwd_from, bwd_from, start, goal, meeting) -> list[tuple]:
    """
    Stitch together the two half-paths at *meeting*.

    Forward  half: start   → meeting  (via fwd_from, traced then reversed)
    Backward half: meeting → goal     (via bwd_from, already in correct order)
    """
    # Forward: start → meeting
    fwd_path = _trace(fwd_from, start, meeting)

    # Backward: meeting → goal
    # bwd_from[meeting] is the next node toward goal; walk until None.
    # The chain is naturally in meeting → goal order — do NOT reverse.
    bwd_path = []
    node = bwd_from.get(meeting)
    while node is not None:
        bwd_path.append(node)
        node = bwd_from.get(node)
    # FIX: removed bwd_path.reverse() — the list is already goal-ward.

    return fwd_path + bwd_path


def bidirectional(grid):
    """
    Bidirectional BFS generator.

    Parameters
    ----------
    grid : Grid   Shared grid object.

    Yields
    ------
    dict  Algorithm state snapshot.
    """
    start = grid.start_node.pos
    goal  = grid.target_node.pos

    # Forward BFS state
    fwd_queue   = deque([start])
    fwd_from    = {start: None}
    fwd_visited = {start}

    # Backward BFS state
    bwd_queue   = deque([goal])
    bwd_from    = {goal: None}
    bwd_visited = {goal}

    fwd_frontier = {start}
    bwd_frontier = {goal}

    def _snapshot(meeting=None, path=None, done=False, found=False):
        return {
            "frontier"     : frozenset(fwd_frontier | bwd_frontier),
            "frontier_fwd" : frozenset(fwd_frontier),
            "frontier_bwd" : frozenset(bwd_frontier),
            "explored"     : frozenset(fwd_visited | bwd_visited),
            "path"         : path,
            "done"         : done,
            "found"        : found,
        }

    # Early exit: start == goal
    if start == goal:
        yield _snapshot(meeting=start, path=[start], done=True, found=True)
        return

    while fwd_queue or bwd_queue:

        # ── Forward step ───────────────────────────────────────────────
        if fwd_queue:
            current = fwd_queue.popleft()
            fwd_frontier.discard(current)

            r, c = current
            node = grid.node(r, c)
            for nb in grid.neighbours(node):
                nb_pos = nb.pos
                if nb_pos not in fwd_visited:
                    fwd_visited.add(nb_pos)
                    fwd_from[nb_pos] = current
                    fwd_queue.append(nb_pos)
                    fwd_frontier.add(nb_pos)

                    # ── Intersection check ─────────────────────────────
                    if nb_pos in bwd_visited:
                        path = _build_path(fwd_from, bwd_from, start, goal, nb_pos)
                        yield _snapshot(meeting=nb_pos, path=path,
                                        done=True, found=True)
                        return

            yield _snapshot()

        # ── Backward step ──────────────────────────────────────────────
        if bwd_queue:
            current = bwd_queue.popleft()
            bwd_frontier.discard(current)

            r, c = current
            node = grid.node(r, c)
            for nb in grid.neighbours(node):
                nb_pos = nb.pos
                if nb_pos not in bwd_visited:
                    bwd_visited.add(nb_pos)
                    bwd_from[nb_pos] = current
                    bwd_queue.append(nb_pos)
                    bwd_frontier.add(nb_pos)

                    # ── Intersection check ─────────────────────────────
                    if nb_pos in fwd_visited:
                        path = _build_path(fwd_from, bwd_from, start, goal, nb_pos)
                        yield _snapshot(meeting=nb_pos, path=path,
                                        done=True, found=True)
                        return

            yield _snapshot()

    # ── Both queues exhausted — no path ────────────────────────────────
    yield _snapshot(path=[], done=True, found=False)