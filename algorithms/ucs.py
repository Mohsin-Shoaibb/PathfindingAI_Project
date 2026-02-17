import heapq


def _reconstruct(came_from: dict, start: tuple, goal: tuple) -> list[tuple]:
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    if path and path[0] == start:
        return path
    return []


def ucs(grid):
    """
    Uniform-Cost Search — expands the lowest cumulative cost node first.
    Finds the optimal path when cells have different weights.
    Yields state snapshots: frontier, explored, path, done, found.
    """
    start = grid.start_node.pos
    goal  = grid.target_node.pos

    counter     = 0                      # tie-breaker so heapq never compares Node objects
    heap        = [(0, counter, start)]  # (cost, counter, pos)
    came_from   = {start: None}
    cost_so_far = {start: 0}
    explored    = set()
    frontier    = {start}

    while heap:
        cost, _, current = heapq.heappop(heap)
        frontier.discard(current)

        # Skip stale heap entries — node was already expanded at a lower cost
        if current in explored:
            continue
        explored.add(current)

        yield {
            "frontier" : frozenset(frontier),
            "explored" : frozenset(explored),
            "path"     : None,
            "done"     : False,
            "found"    : False,
        }

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

        r, c = current
        node = grid.node(r, c)
        for nb in grid.neighbours(node):
            nb_pos   = nb.pos
            new_cost = cost_so_far[current] + nb.weight

            # Relaxation: only push if we found a cheaper route to this neighbour
            if nb_pos not in cost_so_far or new_cost < cost_so_far[nb_pos]:
                cost_so_far[nb_pos] = new_cost
                came_from[nb_pos]   = current
                counter += 1
                heapq.heappush(heap, (new_cost, counter, nb_pos))
                frontier.add(nb_pos)

    yield {
        "frontier" : frozenset(),
        "explored" : frozenset(explored),
        "path"     : [],
        "done"     : True,
        "found"    : False,
    }