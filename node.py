class Node:
    """Represents a single cell in the grid"""
    def __init__(self, row, col, node_type='empty'):
        self.row = row
        self.col = col
        self.node_type = node_type  # 'empty', 'wall', 'start', 'target', 'dynamic_obstacle'
        self.g_cost = float('inf')  # Cost from start (for UCS)
        self.parent = None
        self.visited = False
        self.in_frontier = False
        
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __lt__(self, other):
        # For priority queue comparison (UCS)
        return self.g_cost < other.g_cost
    
    def reset_search_state(self):
        """Reset node state for new search"""
        self.g_cost = float('inf')
        self.parent = None
        self.visited = False
        self.in_frontier = False