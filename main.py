import sys
import time
import pygame

from grid import Grid
from algorithms import bfs, dfs, ucs, dls, iddfs, bidirectional

#  WINDOW & GRID  —  SCREEN_* derives automatically; do not set manually
TITLE        = "OG Path hunter"

GRID_ROWS    = 20          # rows in the maze
GRID_COLS    = 30          # columns in the maze
CELL_SIZE    = 30          # pixels per cell

SIDEBAR_W    = 340         # left panel width
TOP_BAR_H    = 64          # title / status bar height
GRID_MARGIN  = 14          # gap between sidebar and grid

SCREEN_W = SIDEBAR_W + GRID_COLS * CELL_SIZE + GRID_MARGIN * 2
SCREEN_H = TOP_BAR_H + GRID_ROWS * CELL_SIZE + GRID_MARGIN * 2

SCROLL_STEP  = 30          # pixels scrolled per wheel tick / arrow key

#  SIDEBAR LAYOUT  —  each SEC_*_Y is the top edge of that section.
#  Changing a Y shifts the whole section; nothing else needs updating.

SX = 14                        # left margin for all sidebar elements
SW = SIDEBAR_W - SX * 2        # usable content width

#  Algorithm selector 
SEC_ALGO_Y       = 6
SEC_ALGO_BTN_H   = 34
SEC_ALGO_BTN_GAP = 5

#  Map editing tools 
SEC_EDIT_Y       = 290
SEC_EDIT_BTN_H   = 34
SEC_EDIT_BTN_GAP = 5

#  DLS depth limit slider 
SEC_DLS_Y             = 572
SEC_DLS_SLIDER_OFFSET = 22     # slider sits this far below the section header

#  Animation speed slider 
SEC_SPEED_Y             = 640
SEC_SPEED_SLIDER_OFFSET = 22

#  Kept for layout reference (currently unused) 
SEC_DISPLAY_Y          = 782
SEC_DISPLAY_BTN_H      = 34
SEC_DISPLAY_BTN_OFFSET = 20

#  Action buttons 
SEC_START_Y = 842
SEC_START_H = 46              # taller than other buttons for prominence

SEC_RESET_Y = 898
SEC_RESET_H = 34

#  Colour legend 
SEC_LEGEND_Y     = 950
SEC_LEGEND_ROW_H = 24

#  TOP-BAR ANCHORS
#  TITLE / STATUS left-aligned from grid edge; STATS right-aligned
TOPBAR_TITLE_X  = SIDEBAR_W + GRID_MARGIN
TOPBAR_TITLE_Y  = 8
TOPBAR_STATUS_X = SIDEBAR_W + GRID_MARGIN
TOPBAR_STATUS_Y = 36
TOPBAR_STATS_X  = SCREEN_W - 14    # right edge anchor
TOPBAR_STATS_Y  = 22

#  FONT SIZES  —  change one value to resize only that element
FONT_TITLE_SIZE   = 18
FONT_SECTION_SIZE = 12
FONT_BTN_SIZE     = 13
FONT_SLIDER_SIZE  = 12
FONT_SMALL_SIZE   = 12
FONT_CELL_SIZE    = 11    # S / T labels inside grid cells
FONT_STATUS_SIZE  = 13

#  COLOURS  —  ACCENT=highlight  ACCENT2=erase/reset  ACCENT3=success
C_BG         = (  8,  12,  24)
C_PANEL      = ( 14,  20,  40)
C_PANEL2     = ( 20,  30,  56)
C_BORDER     = ( 30,  50,  90)

C_ACCENT     = (  0, 210, 255)   # cyan  — active selection
C_ACCENT2    = (255,  70, 170)   # magenta — reset / erase
C_ACCENT3    = ( 60, 230, 130)   # green — start / found

C_TEXT       = (225, 235, 255)
C_TEXT_DIM   = (130, 160, 210)
C_TEXT_MUTED = ( 75, 100, 148)

C_EMPTY      = ( 16,  24,  48)
C_EMPTY_DARK = ( 10,  15,  32)
C_WALL       = (  8,  12,  22)
C_WALL_GLOW  = ( 42,  62, 105)   # thin border drawn on top of wall cells
C_START      = ( 30, 220,  80)
C_TARGET     = (255,  60, 100)
C_FRONTIER   = ( 30,  90, 220)   # forward frontier (all algos except bidir)
C_FRONTIER2  = ( 60, 140, 255)   # backward frontier (bidirectional only)
C_EXPLORED   = ( 18,  48, 110)
C_PATH       = (255, 195,  35)

#  ALGORITHM REGISTRY  —  (button label, full name, generator function)
#  Add a new entry here to expose a new algorithm in the sidebar.
ALGO_LIST = [
    ("BFS",   "Breadth-First Search",    bfs),
    ("DFS",   "Depth-First Search",      dfs),
    ("UCS",   "Uniform-Cost Search",     ucs),
    ("DLS",   "Depth-Limited Search",    dls),
    ("IDDFS", "Iterative Deepening DFS", iddfs),
    ("BIDIR", "Bidirectional Search",    bidirectional),
]

#  DRAWING HELPERS
def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB colours; used for pulsing frontier cells."""
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

def rrect(surf, color, rect, r=7):
    pygame.draw.rect(surf, color, rect, border_radius=r)

def rrect_border(surf, color, rect, width, r=7):
    pygame.draw.rect(surf, color, rect, width, border_radius=r)

def put_text(surf, text, font, color, x, y, anchor="left"):
    """Render text at (x, y). anchor='right' or 'center' shifts the origin."""
    img = font.render(text, True, color)
    if anchor == "center": x -= img.get_width() // 2
    elif anchor == "right": x -= img.get_width()
    surf.blit(img, (x, y))
    return img.get_width()

def section_header(surf, font, text, x, y):
    """Draw a labelled divider — title on the left, horizontal rule extending right."""
    img = font.render(text, True, C_TEXT_DIM)
    surf.blit(img, (x, y))
    lx = x + img.get_width() + 10
    ly = y + img.get_height() // 2
    pygame.draw.line(surf, C_BORDER, (lx, ly), (SIDEBAR_W - x, ly), 1)

#  BUTTON WIDGET
class Button:
    def __init__(self, x, y, w, h, label,
                 bg=C_PANEL2, fg=C_TEXT, accent=C_ACCENT, font=None):
        self.rect    = pygame.Rect(x, y, w, h)
        self.label   = label
        self.bg, self.fg, self.accent = bg, fg, accent
        self.font    = font
        self.active  = False    # True when this button is the current selection
        self.hovered = False

    def draw(self, surf, offset_y=0):
        """offset_y is the scroll + top-bar shift applied at render time."""
        r = self.rect.move(0, offset_y)
        if self.active:
            bg, brd, fg = lerp_color(self.accent, self.bg, 0.38), self.accent, self.accent
        elif self.hovered:
            bg, brd, fg = lerp_color(self.bg, self.accent, 0.18), self.accent, self.fg
        else:
            bg, brd, fg = self.bg, C_BORDER, self.fg
        rrect(surf, bg, r)
        rrect_border(surf, brd, r, 1)
        if self.font:
            img = self.font.render(self.label, True, fg)
            surf.blit(img, (r.centerx - img.get_width() // 2,
                            r.centery  - img.get_height() // 2))

    def handle(self, event, offset_y=0):
        """Returns True on the frame the button is clicked. offset_y must match draw()."""
        shifted = self.rect.move(0, offset_y)
        if event.type == pygame.MOUSEMOTION:
            self.hovered = shifted.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if shifted.collidepoint(event.pos):
                return True
        return False

#  SLIDER WIDGET
class Slider:
    def __init__(self, x, y, w, label, lo, hi, val, fmt="{:.3f}", font=None):
        self.track = pygame.Rect(x, y, w, 6)
        self.label = label
        self.lo, self.hi = lo, hi
        self.val   = val
        self.fmt   = fmt
        self.font  = font
        self._drag = False

    @property
    def norm(self):
        """Normalised knob position in [0, 1]."""
        return (self.val - self.lo) / (self.hi - self.lo)

    @norm.setter
    def norm(self, t):
        self.val = self.lo + max(0.0, min(1.0, t)) * (self.hi - self.lo)

    def draw(self, surf, offset_y=0):
        tr = self.track.move(0, offset_y)
        rrect(surf, C_BORDER, tr, 3)
        fw = max(0, int(tr.width * self.norm))
        if fw > 0:
            rrect(surf, C_ACCENT, pygame.Rect(tr.x, tr.y, fw, tr.h), 3)
        kx = tr.x + int(tr.width * self.norm)
        ky = tr.centery
        pygame.draw.circle(surf, C_ACCENT, (kx, ky), 9)
        pygame.draw.circle(surf, C_BG,     (kx, ky), 5)
        if self.font:
            lbl  = self.font.render(self.label, True, C_TEXT_DIM)
            vimg = self.font.render(self.fmt.format(self.val), True, C_ACCENT)
            surf.blit(lbl,  (tr.x, tr.y - 20))
            surf.blit(vimg, (tr.right - vimg.get_width(), tr.y - 20))

    def handle(self, event, offset_y=0):
        tr = self.track.move(0, offset_y)
        kx = tr.x + int(tr.width * self.norm)
        ky = tr.centery
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs(event.pos[0]-kx) < 14 and abs(event.pos[1]-ky) < 14:
                self._drag = True
            elif tr.collidepoint(event.pos):
                self.norm = (event.pos[0] - tr.x) / tr.width
        if event.type == pygame.MOUSEBUTTONUP:
            self._drag = False
        if event.type == pygame.MOUSEMOTION and self._drag:
            self.norm = (event.pos[0] - tr.x) / tr.width

#  MAIN APPLICATION
class App:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()

        # One font object per role — avoids re-creating fonts every frame
        self.f_title   = pygame.font.SysFont("consolas", FONT_TITLE_SIZE,   bold=True)
        self.f_section = pygame.font.SysFont("consolas", FONT_SECTION_SIZE, bold=True)
        self.f_btn     = pygame.font.SysFont("consolas", FONT_BTN_SIZE,     bold=True)
        self.f_slider  = pygame.font.SysFont("consolas", FONT_SLIDER_SIZE)
        self.f_small   = pygame.font.SysFont("consolas", FONT_SMALL_SIZE)
        self.f_cell    = pygame.font.SysFont("consolas", FONT_CELL_SIZE,    bold=True)
        self.f_status  = pygame.font.SysFont("consolas", FONT_STATUS_SIZE,  bold=True)

        self.grid         = Grid(GRID_ROWS, GRID_COLS)
        self.algo_idx     = 0           # index into ALGO_LIST
        self.generator    = None        # active algorithm generator; None when idle
        self.running      = False       # True while stepping through the algorithm
        self.done         = False       # True after the algorithm finishes
        self.steps        = 0           # frames stepped since last start
        self.path_len     = 0           # nodes in the final path (0 if not found)
        self.edit_mode    = None        # active tool: 'start' 'target' 'wall' 'erase'
        self.current_path = []          # last found path positions
        self.scroll_y     = 0           # sidebar scroll offset (≤ 0)
        self.status = "Select algorithm  →  draw map  →  press  ▶ START"

        self._build_sidebar()

    #  BUILD SIDEBAR
    def _build_sidebar(self):

        # One button per algorithm; active flag highlights the current selection
        self.algo_btns = []
        y = SEC_ALGO_Y + 20          # 20 px reserved for the section header text
        for i, (short, full, _) in enumerate(ALGO_LIST):
            btn = Button(SX, y, SW, SEC_ALGO_BTN_H,
                         f"{short}  —  {full}", font=self.f_btn)
            btn.active = (i == self.algo_idx)
            self.algo_btns.append(btn)
            y += SEC_ALGO_BTN_H + SEC_ALGO_BTN_GAP

        # Clicking a tool activates it; clicking the active tool deactivates it
        edit_items = [
            ("Set Start  (S)",   "start",  C_START),
            ("Set Target  (T)",  "target", C_TARGET),
            ("Draw Walls",       "wall",   C_WALL_GLOW),
            ("Erase Walls",      "erase",  C_ACCENT2),
        ]
        self.edit_btns = {}
        y = SEC_EDIT_Y + 20
        for label, mode, col in edit_items:
            btn = Button(SX, y, SW, SEC_EDIT_BTN_H,
                         label, font=self.f_btn, accent=col)
            self.edit_btns[mode] = btn
            y += SEC_EDIT_BTN_H + SEC_EDIT_BTN_GAP

        # Depth limit only affects DLS; ignored by all other algorithms
        self.dls_slider = Slider(
            SX, SEC_DLS_Y + SEC_DLS_SLIDER_OFFSET, SW,
            "DLS Depth Limit", 1, 50, 15, "{:.0f}", self.f_slider
        )

        # Seconds between algorithm steps — lower = faster animation
        self.speed_slider = Slider(
            SX, SEC_SPEED_Y + SEC_SPEED_SLIDER_OFFSET, SW,
            "Step Delay (s)", 0.001, 0.25, 0.04, "{:.3f}", self.f_slider
        )

        self.btn_start = Button(
            SX, SEC_START_Y, SW, SEC_START_H,
            "▶   START",
            bg=(10, 30, 16), accent=C_ACCENT3, font=self.f_btn
        )

        self.btn_reset = Button(
            SX, SEC_RESET_Y, SW, SEC_RESET_H,
            "⟳   RESET ALL",
            bg=(30, 10, 16), accent=C_ACCENT2, font=self.f_btn
        )

        self._legend = [
            (C_START,     "Start node  (S)"),
            (C_TARGET,    "Target node  (T)"),
            (C_WALL,      "Static wall"),
            (C_FRONTIER,  "Frontier  (forward)"),
            (C_FRONTIER2, "Frontier  (backward)"),
            (C_EXPLORED,  "Explored"),
            (C_PATH,      "Final path"),
        ]

        # Total virtual height of sidebar content — used to cap scroll range
        self._SIDEBAR_H = (SEC_LEGEND_Y + 20
                           + len(self._legend) * SEC_LEGEND_ROW_H + 16)

    #  SCROLL
    def _max_scroll(self):
        """Maximum downward scroll before content runs off the bottom."""
        return max(0, self._SIDEBAR_H - (SCREEN_H - TOP_BAR_H + 450))

    #  GRID HELPERS
    def _grid_origin(self):
        """Pixel coordinate of the top-left corner of the grid."""
        return (SIDEBAR_W + GRID_MARGIN, TOP_BAR_H + GRID_MARGIN)

    def _cell_rect(self, r, c):
        """Screen rect for cell (r, c). 1 px gap between adjacent cells."""
        ox, oy = self._grid_origin()
        return pygame.Rect(ox + c*CELL_SIZE, oy + r*CELL_SIZE,
                           CELL_SIZE - 1, CELL_SIZE - 1)

    def _pixel_to_cell(self, px, py):
        """Convert a screen pixel to (row, col), or None if outside the grid."""
        ox, oy = self._grid_origin()
        c = (px - ox) // CELL_SIZE
        r = (py - oy) // CELL_SIZE
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            return (r, c)
        return None

    #  SEARCH CONTROL
    def _start_search(self):
        """Reset visual state and create a fresh generator for the selected algorithm."""
        self.grid.reset_search()
        self.current_path = []
        self.done = False; self.running = True
        short, full, fn = ALGO_LIST[self.algo_idx]
        lim = int(self.dls_slider.val)
        # DLS requires an explicit depth limit; all other algorithms ignore it
        self.generator = fn(self.grid, lim) if short == "DLS" else fn(self.grid)
        self.status = f"Running  {full} …"

    def _reset(self):
        """Stop any running search and wipe the grid back to blank."""
        self.generator = None
        self.running = self.done = False
        self.current_path = []
        self.steps = self.path_len = 0
        self.grid.full_reset()
        self.status = "Grid reset — draw a map and press  ▶ START"

    def _step(self):
        """Pull one frame from the generator and refresh cell visual states."""
        if not self.generator: return
        try:
            snap = next(self.generator)
        except StopIteration:
            self._finish(False); return

        self.steps += 1
        self._apply_snapshot(snap)

        if snap.get("done"):
            if snap.get("found"):
                self.current_path = snap.get("path", [])
                self._finish(True, self.current_path)
            else:
                self._finish(False)
            return

    def _apply_snapshot(self, snap):
        """Map the algorithm snapshot to per-cell visual states for rendering."""
        fwd  = snap.get("frontier_fwd") or snap.get("frontier", frozenset())
        bwd  = snap.get("frontier_bwd", frozenset())    # non-empty for bidirectional only
        expl = snap.get("explored", frozenset())
        path = snap.get("path")
        for nd in self.grid.all_nodes():
            p = nd.pos
            if nd is self.grid.start_node or nd is self.grid.target_node: continue
            if   nd.is_wall:          nd.state = "wall"
            elif path and p in path:  nd.state = "path"
            elif p in expl:           nd.state = "explored"
            elif p in bwd:            nd.state = "frontier2"
            elif p in fwd:            nd.state = "frontier"
            else:                     nd.state = "empty"

    def _finish(self, found, path=None):
        """Mark search complete and write the result summary to the status bar."""
        self.running = False; self.done = True; self.generator = None
        short = ALGO_LIST[self.algo_idx][0]
        if found and path:
            self.path_len = len(path); self.current_path = path
            self.status = f"✓  {short}  |  Steps: {self.steps}  |  Path: {self.path_len}"
        else:
            self.status = f"✗  {short}  —  No path found!   Steps: {self.steps}"

    #  DRAWING
    def _draw_top_bar(self):
        pygame.draw.rect(self.screen, C_PANEL, pygame.Rect(0, 0, SCREEN_W, TOP_BAR_H))
        pygame.draw.line(self.screen, C_BORDER, (0, TOP_BAR_H-1), (SCREEN_W, TOP_BAR_H-1), 1)

        put_text(self.screen, TITLE, self.f_title, C_ACCENT,
                 TOPBAR_TITLE_X, TOPBAR_TITLE_Y)

        # Green = found, magenta = failed, dim = running or idle
        col = (C_ACCENT3 if "✓" in self.status
               else C_ACCENT2 if any(c in self.status for c in ("✗","⚡"))
               else C_TEXT_DIM)
        put_text(self.screen, self.status, self.f_status, col,
                 TOPBAR_STATUS_X, TOPBAR_STATUS_Y)

        put_text(self.screen, f"Steps: {self.steps}    Path: {self.path_len}",
                 self.f_small, C_TEXT_DIM,
                 TOPBAR_STATS_X, TOPBAR_STATS_Y, anchor="right")

    def _draw_sidebar(self):
        pygame.draw.rect(self.screen, C_PANEL, pygame.Rect(0, 0, SIDEBAR_W, SCREEN_H))
        pygame.draw.line(self.screen, C_BORDER,
                         (SIDEBAR_W-1, TOP_BAR_H), (SIDEBAR_W-1, SCREEN_H), 1)

        # Clip so scrolled content never bleeds into the top bar
        self.screen.set_clip(pygame.Rect(0, TOP_BAR_H, SIDEBAR_W, SCREEN_H - TOP_BAR_H))

        # B(y): converts sidebar-local Y to screen Y, accounting for scroll
        def B(y): return TOP_BAR_H + self.scroll_y + y

        section_header(self.screen, self.f_section, "ALGORITHM", SX, B(SEC_ALGO_Y))
        for i, btn in enumerate(self.algo_btns):
            btn.active = (i == self.algo_idx)
            btn.draw(self.screen, B(SEC_ALGO_Y))

        section_header(self.screen, self.f_section, "EDIT MODE", SX, B(SEC_EDIT_Y))
        for mode, btn in self.edit_btns.items():
            btn.active = (self.edit_mode == mode)
            btn.draw(self.screen, B(SEC_EDIT_Y - 290))

        self.dls_slider.draw(self.screen, B(SEC_DLS_Y - 645))
        self.speed_slider.draw(self.screen, B(SEC_SPEED_Y - 720))

        self.btn_start.draw(self.screen, B(SEC_START_Y - 1080))
        self.btn_reset.draw(self.screen, B(SEC_RESET_Y - 1140))

        section_header(self.screen, self.f_section, "COLOUR LEGEND", SX, B(SEC_LEGEND_Y))
        ly = B(SEC_LEGEND_Y + 20)
        for color, lbl in self._legend:
            pygame.draw.rect(self.screen, color,
                             pygame.Rect(SX, ly + 3, 18, 16), border_radius=3)
            put_text(self.screen, lbl, self.f_small, C_TEXT_DIM, SX + 28, ly)
            ly += SEC_LEGEND_ROW_H

        self.screen.set_clip(None)

        # Thin scroll indicator on the sidebar's right edge
        max_s = self._max_scroll()
        if max_s > 0:
            vh    = SCREEN_H - TOP_BAR_H
            bar_h = max(28, int(vh * vh / self._SIDEBAR_H))
            t     = (-self.scroll_y) / max_s
            bar_y = TOP_BAR_H + int(t * (vh - bar_h))
            pygame.draw.rect(self.screen, C_BORDER,
                             pygame.Rect(SIDEBAR_W - 5, bar_y, 4, bar_h), border_radius=2)

    def _draw_grid(self):
        ox, oy = self._grid_origin()
        # Dark background rect gives the grid a subtle inset border
        pygame.draw.rect(self.screen, C_EMPTY_DARK,
                         pygame.Rect(ox-2, oy-2,
                                     GRID_COLS*CELL_SIZE+4,
                                     GRID_ROWS*CELL_SIZE+4), border_radius=5)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                self._draw_cell(self.grid.node(r, c), self._cell_rect(r, c))

    def _draw_cell(self, nd, rect):
        """Colour each cell by its current state; frontier cells pulse over time."""
        state = nd.state
        t = (time.time() * 2.5) % 1.0   # 0→1 cycle used for frontier pulse animation
        if   state == "wall":      color = C_WALL
        elif state == "start":     color = C_START
        elif state == "target":    color = C_TARGET
        elif state == "frontier":  color = lerp_color(C_FRONTIER, C_FRONTIER2, t)
        elif state == "frontier2": color = lerp_color(C_FRONTIER2, C_FRONTIER, t)
        elif state == "explored":  color = C_EXPLORED
        elif state == "path":      color = C_PATH
        else:                      color = C_EMPTY

        pygame.draw.rect(self.screen, color, rect, border_radius=3)
        if state == "wall":
            # Subtle glow border distinguishes walls from the dark background
            pygame.draw.rect(self.screen, C_WALL_GLOW, rect, 1, border_radius=3)

        if state in ("start", "target"):
            img = self.f_cell.render("S" if state == "start" else "T", True, C_BG)
            self.screen.blit(img, (rect.centerx - img.get_width()//2,
                                   rect.centery - img.get_height()//2))

    #  EVENTS
    def _handle_events(self):
        # base is added to every widget's stored rect.y to get the true screen Y
        base = TOP_BAR_H + self.scroll_y

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE: self.edit_mode = None
                if k == pygame.K_SPACE and not self.running: self._start_search()
                if k == pygame.K_r:      self._reset()
                if k == pygame.K_UP:
                    self.scroll_y = min(0, self.scroll_y + SCROLL_STEP)
                if k == pygame.K_DOWN:
                    self.scroll_y = max(-self._max_scroll(), self.scroll_y - SCROLL_STEP)

            if event.type == pygame.MOUSEWHEEL:
                if pygame.mouse.get_pos()[0] < SIDEBAR_W:
                    self.scroll_y += event.y * SCROLL_STEP
                    self.scroll_y = max(-self._max_scroll(), min(0, self.scroll_y))

            for i, btn in enumerate(self.algo_btns):
                if btn.handle(event, base + SEC_ALGO_Y):
                    self.algo_idx = i
                    for b in self.algo_btns: b.active = False
                    btn.active = True

            for mode, btn in self.edit_btns.items():
                if btn.handle(event, base + SEC_EDIT_Y - 290):
                    self.edit_mode = None if self.edit_mode == mode else mode

            self.dls_slider.handle(event,   base + SEC_DLS_Y - 645)
            self.speed_slider.handle(event, base + SEC_SPEED_Y - 720)

            if self.btn_start.handle(event, base + SEC_START_Y - 1080):
                if not self.running: self._start_search()
            if self.btn_reset.handle(event, base + SEC_RESET_Y - 1140):
                self._reset()

            self._handle_grid_mouse(event)

    def _handle_grid_mouse(self, event):
        """Paint cells on click / drag according to the active edit mode."""
        if event.type not in (pygame.MOUSEBUTTONDOWN,
                               pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP): return
        if self.running: return
        btns = pygame.mouse.get_pressed()
        if event.type == pygame.MOUSEMOTION and not btns[0]: return
        cell = self._pixel_to_cell(*event.pos)
        if cell is None: return
        r, c = cell
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if   self.edit_mode == "start":  self.grid.set_start(r,c);  self.edit_mode = None
            elif self.edit_mode == "target": self.grid.set_target(r,c); self.edit_mode = None
            elif self.edit_mode == "wall":   self.grid.place_wall(r,c)
            elif self.edit_mode == "erase":  self.grid.erase_wall(r,c)
        elif event.type == pygame.MOUSEMOTION and btns[0]:
            if   self.edit_mode == "wall":   self.grid.place_wall(r,c)
            elif self.edit_mode == "erase":  self.grid.erase_wall(r,c)

    #  MAIN LOOP

    def run(self):
        last_step = 0.0
        while True:
            self._handle_events()
            now = time.time()
            # Advance one algorithm step when the chosen delay has elapsed
            if self.running and (now - last_step) >= self.speed_slider.val:
                self._step(); last_step = now
            self.screen.fill(C_BG)
            self._draw_grid()
            self._draw_sidebar()
            self._draw_top_bar()    # drawn last so it always renders on top
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    App().run()