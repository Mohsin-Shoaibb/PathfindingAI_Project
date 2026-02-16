import random
from node import Node

class Grid:
    """Manages the grid environment"""
    def __init__(self, rows, cols, obstacle_probability=0.001):
        self.rows = rows
        self.cols = cols
        self.obstacle_probability = obstacle_probability
        self.grid = [[Node(r, c) for c in range(cols)] for r in range(rows)]
        self.start = None
        self.target = None
        self.dynamic_obstacles = []
        
    def set_start(self, row, col):
        """Set the start position"""
        if self.start:
            self.grid[self.start[0]][self.start[1]].node_type = 'empty'
        self.start = (row, col)
        self.grid[row][col].node_type = 'start'
        self.grid[row][col].g_cost = 0
        
    def set_target(self, row, col):
        """Set the target position"""
        if self.target:
            self.grid[self.target[0]][self.target[1]].node_type = 'empty'
        self.target = (row, col)
        self.grid[row][col].node_type = 'target'
        
    def set_wall(self, row, col):
        """Set a wall at position"""
        if (row, col) != self.start and (row, col) != self.target:
            self.grid[row][col].node_type = 'wall'
            
    def remove_wall(self, row, col):
        """Remove a wall at position"""
        if self.grid[row][col].node_type == 'wall':
            self.grid[row][col].node_type = 'empty'
    
    def spawn_dynamic_obstacle(self):
        """Randomly spawn a dynamic obstacle"""
        if random.random() < self.obstacle_probability:
            # Find empty cells
            empty_cells = []
            for r in range(self.rows):
                for c in range(self.cols):
                    node = self.grid[r][c]
                    if node.node_type == 'empty' and not node.visited and not node.in_frontier:
                        empty_cells.append((r, c))
            
            if empty_cells:
                r, c = random.choice(empty_cells)
                self.grid[r][c].node_type = 'dynamic_obstacle'
                self.dynamic_obstacles.append((r, c))
                return (r, c)
        return None
    
    def get_neighbors(self, node):
        """Get valid neighbors in clockwise order with all diagonals"""
        neighbors = []
        r, c = node.row, node.col
        
        # Clockwise order with ALL diagonals:
        # Up, Top-Right, Right, Bottom-Right, Bottom, Bottom-Left, Left, Top-Left
        directions = [
            (-1, 0),   # Up
            (-1, 1),   # Top-Right
            (0, 1),    # Right
            (1, 1),    # Bottom-Right
            (1, 0),    # Bottom
            (1, -1),   # Bottom-Left
            (0, -1),   # Left
            (-1, -1)   # Top-Left
        ]
        
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            
            # Check bounds
            if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
                neighbor = self.grid[new_r][new_c]
                
                # Check if not a wall or dynamic obstacle
                if neighbor.node_type not in ['wall', 'dynamic_obstacle']:
                    neighbors.append(neighbor)
        
        return neighbors
    
    def reset_search_states(self):
        """Reset all nodes for a new search"""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].reset_search_state()
        
        # Reset start node cost
        if self.start:
            self.grid[self.start[0]][self.start[1]].g_cost = 0
    
    def clear_dynamic_obstacles(self):
        """Clear all dynamic obstacles"""
        for r, c in self.dynamic_obstacles:
            if self.grid[r][c].node_type == 'dynamic_obstacle':
                self.grid[r][c].node_type = 'empty'
        self.dynamic_obstacles = []