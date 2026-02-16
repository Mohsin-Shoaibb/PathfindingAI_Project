import pygame
import sys
from grid import Grid
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.ucs import ucs
from algorithms.dls import dls
from algorithms.iddfs import iddfs
from algorithms.bidirectional import bidirectional_search

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
GRID_ROWS = 30
GRID_COLS = 40
CELL_SIZE = 20
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 128, 0)
DARK_BLUE = (0, 0, 128)

# Color scheme
COLORS = {
    'empty': WHITE,
    'wall': BLACK,
    'start': GREEN,
    'target': RED,
    'frontier': CYAN,
    'visited': YELLOW,
    'path': BLUE,
    'dynamic_obstacle': ORANGE,
    'frontier_both': MAGENTA  # For bidirectional search
}

class PathfindingGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("GOOD PERFORMANCE TIME APP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        # Grid setup
        self.grid = Grid(GRID_ROWS, GRID_COLS, obstacle_probability=0.002)
        
        # Default positions
        self.grid.set_start(5, 5)
        self.grid.set_target(GRID_ROWS - 5, GRID_COLS - 5)
        
        # State
        self.mode = 'wall'  # 'wall', 'erase', 'start', 'target'
        self.drawing = False
        self.running = True
        self.searching = False
        self.current_algorithm = 'BFS'
        self.delay = 20  # milliseconds between steps
        
        # Algorithm results
        self.path = []
        self.stats = {
            'nodes_explored': 0,
            'path_length': 0,
            'search_complete': False
        }
        
    def draw_grid(self):
        """Draw the grid and all nodes"""
        # Draw cells
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                node = self.grid.grid[r][c]
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                
                # Determine color
                if node.node_type == 'start':
                    color = COLORS['start']
                elif node.node_type == 'target':
                    color = COLORS['target']
                elif node.node_type == 'wall':
                    color = COLORS['wall']
                elif node.node_type == 'dynamic_obstacle':
                    color = COLORS['dynamic_obstacle']
                elif (r, c) in [(n.row, n.col) for n in self.path]:
                    color = COLORS['path']
                elif node.in_frontier:
                    color = COLORS['frontier']
                elif node.visited:
                    color = COLORS['visited']
                else:
                    color = COLORS['empty']
                
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
        
    def draw_ui(self):
        """Draw UI elements and controls"""
        ui_x = GRID_WIDTH + 20
        y_offset = 20
        
        # Title
        title = self.title_font.render("GOOD PERFORMANCE TIME APP", True, BLACK)
        self.screen.blit(title, (ui_x, y_offset))
        y_offset += 50
        
        # Algorithm selection
        algo_text = self.font.render(f"Algorithm: {self.current_algorithm}", True, BLACK)
        self.screen.blit(algo_text, (ui_x, y_offset))
        y_offset += 30
        
        # Mode
        mode_text = self.font.render(f"Mode: {self.mode.upper()}", True, BLACK)
        self.screen.blit(mode_text, (ui_x, y_offset))
        y_offset += 30
        
        # Stats
        stats_title = self.font.render("--- Statistics ---", True, BLACK)
        self.screen.blit(stats_title, (ui_x, y_offset))
        y_offset += 30
        
        nodes_text = self.font.render(f"Nodes Explored: {self.stats['nodes_explored']}", True, BLACK)
        self.screen.blit(nodes_text, (ui_x, y_offset))
        y_offset += 25
        
        path_text = self.font.render(f"Path Length: {self.stats['path_length']}", True, BLACK)
        self.screen.blit(path_text, (ui_x, y_offset))
        y_offset += 25
        
        status = "Complete!" if self.stats['search_complete'] else "Running..." if self.searching else "Ready"
        status_text = self.font.render(f"Status: {status}", True, BLACK)
        self.screen.blit(status_text, (ui_x, y_offset))
        y_offset += 40
        
        # Controls
        controls_title = self.font.render("--- Controls ---", True, BLACK)
        self.screen.blit(controls_title, (ui_x, y_offset))
        y_offset += 30
        
        controls = [
            "1-6: Select Algorithm",
            "  1: BFS",
            "  2: DFS",
            "  3: UCS",
            "  4: DLS",
            "  5: IDDFS",
            "  6: Bidirectional",
            "",
            "SPACE: Start Search",
            "R: Reset Search",
            "C: Clear Grid",
            "W: Wall Mode",
            "E: Erase Mode",
            "S: Set Start",
            "T: Set Target",
            "+/-: Adjust Speed",
            "",
            "Click & Drag: Draw"
        ]
        
        for line in controls:
            text = self.font.render(line, True, BLACK)
            self.screen.blit(text, (ui_x, y_offset))
            y_offset += 25
        
        # Legend
        y_offset += 20
        legend_title = self.font.render("--- Legend ---", True, BLACK)
        self.screen.blit(legend_title, (ui_x, y_offset))
        y_offset += 30
        
        legend_items = [
            ("Start", COLORS['start']),
            ("Target", COLORS['target']),
            ("Wall", COLORS['wall']),
            ("Frontier", COLORS['frontier']),
            ("Visited", COLORS['visited']),
            ("Path", COLORS['path']),
            ("Dynamic Obs", COLORS['dynamic_obstacle'])
        ]
        
        for label, color in legend_items:
            pygame.draw.rect(self.screen, color, (ui_x, y_offset, 20, 20))
            pygame.draw.rect(self.screen, BLACK, (ui_x, y_offset, 20, 20), 1)
            text = self.font.render(label, True, BLACK)
            self.screen.blit(text, (ui_x + 30, y_offset))
            y_offset += 25
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks on grid"""
        x, y = pos
        if x < GRID_WIDTH and y < GRID_HEIGHT:
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            
            if self.mode == 'wall':
                self.grid.set_wall(row, col)
            elif self.mode == 'erase':
                self.grid.remove_wall(row, col)
            elif self.mode == 'start':
                self.grid.set_start(row, col)
                self.mode = 'wall'
            elif self.mode == 'target':
                self.grid.set_target(row, col)
                self.mode = 'wall'
    
    def reset_search(self):
        """Reset the search state"""
        self.grid.reset_search_states()
        self.grid.clear_dynamic_obstacles()
        self.path = []
        self.stats = {
            'nodes_explored': 0,
            'path_length': 0,
            'search_complete': False
        }
        self.searching = False
    
    def clear_grid(self):
        """Clear all walls and obstacles"""
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid.grid[r][c].node_type == 'wall':
                    self.grid.grid[r][c].node_type = 'empty'
        self.reset_search()
    
    def start_search(self):
        """Start the selected algorithm"""
        if self.searching or not self.grid.start or not self.grid.target:
            return
        
        self.reset_search()
        self.searching = True
        
        # Run algorithm in generator mode for step-by-step visualization
        if self.current_algorithm == 'BFS':
            self.search_generator = bfs(self.grid, self)
        elif self.current_algorithm == 'DFS':
            self.search_generator = dfs(self.grid, self)
        elif self.current_algorithm == 'UCS':
            self.search_generator = ucs(self.grid, self)
        elif self.current_algorithm == 'DLS':
            self.search_generator = dls(self.grid, self, depth_limit=20)
        elif self.current_algorithm == 'IDDFS':
            self.search_generator = iddfs(self.grid, self, max_depth=30)
        elif self.current_algorithm == 'Bidirectional':
            self.search_generator = bidirectional_search(self.grid, self)
    
    def step_search(self):
        """Execute one step of the search"""
        if self.searching:
            try:
                next(self.search_generator)
            except StopIteration:
                self.searching = False
                self.stats['search_complete'] = True
    
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drawing = True
                self.handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    self.handle_mouse_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_search()
                
                elif event.key == pygame.K_r:
                    self.reset_search()
                
                elif event.key == pygame.K_c:
                    self.clear_grid()
                
                elif event.key == pygame.K_w:
                    self.mode = 'wall'
                
                elif event.key == pygame.K_e:
                    self.mode = 'erase'
                
                elif event.key == pygame.K_s:
                    self.mode = 'start'
                
                elif event.key == pygame.K_t:
                    self.mode = 'target'
                
                elif event.key == pygame.K_1:
                    self.current_algorithm = 'BFS'
                    self.reset_search()
                
                elif event.key == pygame.K_2:
                    self.current_algorithm = 'DFS'
                    self.reset_search()
                
                elif event.key == pygame.K_3:
                    self.current_algorithm = 'UCS'
                    self.reset_search()
                
                elif event.key == pygame.K_4:
                    self.current_algorithm = 'DLS'
                    self.reset_search()
                
                elif event.key == pygame.K_5:
                    self.current_algorithm = 'IDDFS'
                    self.reset_search()
                
                elif event.key == pygame.K_6:
                    self.current_algorithm = 'Bidirectional'
                    self.reset_search()
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.delay = max(1, self.delay - 5)
                
                elif event.key == pygame.K_MINUS:
                    self.delay = min(100, self.delay + 5)
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            # Step through search if active
            if self.searching:
                self.step_search()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)
            
            # Add delay during search for visualization
            if self.searching:
                pygame.time.delay(self.delay)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = PathfindingGUI()
    gui.run()