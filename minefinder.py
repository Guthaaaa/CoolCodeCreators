import pygame
import random

# --- CONFIGURATION & COLORS ---
pygame.init()
COLOR_GRASS_L = (170, 215, 81)
COLOR_GRASS_D = (162, 209, 73)
COLOR_HEADER = (74, 117, 44)
COLOR_REVEAL_L = (229, 194, 159)
COLOR_REVEAL_D = (215, 184, 153)
WHITE, BLACK, GOLD = (255, 255, 255), (0, 0, 0), (255, 215, 0)
EXIT_RED = (231, 71, 29)

HEADER_H = 100
font = pygame.font.SysFont("arial", 30, bold=True)
small_font = pygame.font.SysFont("arial", 18, bold=True)

DIFFICULTIES = {
    "1": (10, 10, 10, 50),
    "2": (14, 14, 30, 40),
    "3": (16, 20, 50, 35)
}

# --- GLOBAL EFFECT LISTS ---
particles = []
floating_texts = []

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-3, 3), random.uniform(-3, 3)
        self.life = 255
        self.color = color
    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= 15
        return self.life > 0
    def draw(self, surf):
        s = pygame.Surface((5, 5)); s.set_alpha(self.life); s.fill(self.color)
        surf.blit(s, (self.x, self.y))

class FloatingText:
    def __init__(self, x, y, text):
        self.x, self.y, self.text, self.life = x, y, text, 255
    def update(self):
        self.y -= 1; self.life -= 10
        return self.life > 0

class Cell:
    def __init__(self, r, c, size):
        self.r, self.c, self.size = r, c, size
        self.mine = False
        self.revealed = False
        self.flagged = False
        self.adj_mines = 0

    def draw(self, surf, ox, oy):
        x, y = self.c * self.size + ox, self.r * self.size + HEADER_H + oy
        is_dark = (self.r + self.c) % 2 == 1
        if not self.revealed:
            color = COLOR_GRASS_D if is_dark else COLOR_GRASS_L
            pygame.draw.rect(surf, color, (x, y, self.size, self.size))
            if self.flagged:
                pygame.draw.circle(surf, EXIT_RED, (x + self.size//2, y + self.size//2), self.size//4)
        else:
            color = COLOR_REVEAL_D if is_dark else COLOR_REVEAL_L
            pygame.draw.rect(surf, color, (x, y, self.size, self.size))
            if self.mine:
                pygame.draw.circle(surf, BLACK, (x + self.size//2, y + self.size//2), self.size//3)
            elif self.adj_mines > 0:
                colors = {1: (25, 118, 210), 2: (56, 142, 60), 3: (211, 47, 47), 4: (123, 31, 162)}
                txt = font.render(str(self.adj_mines), True, colors.get(self.adj_mines, BLACK))
                surf.blit(txt, (x + self.size//3, y + self.size//6))

# --- LOGIC FUNCTIONS ---
def setup_mines(board, rows, cols, mine_count, start_r, start_c):
    forbidden = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            forbidden.append((start_r + dr, start_c + dc))
            
    mines = 0
    while mines < mine_count:
        r, c = random.randint(0, rows-1), random.randint(0, cols-1)
        if (r, c) not in forbidden and not board[r][c].mine:
            board[r][c].mine = True; mines += 1
            
    for r in range(rows):
        for c in range(cols):
            if board[r][c].mine: continue
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if board[nr][nc].mine:
                            board[r][c].adj_mines += 1

def iterative_reveal(board, r, c, rows, cols):
    stack, count = [(r, c)], 0
    while stack:
        curr_r, curr_c = stack.pop()
        if not (0 <= curr_r < rows and 0 <= curr_c < cols): continue
        cell = board[curr_r][curr_c]
        if cell.revealed or cell.flagged: continue
        cell.revealed = True; count += 1
        if cell.adj_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    stack.append((curr_r + dr, curr_c + dc))
    return count

def main_game():
    global particles, floating_texts
    # Difficulty Menu
    menu_screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Select Difficulty")
    diff = None
    # --- Updated Difficulty Menu ---
    while diff is None:
        menu_screen.fill(COLOR_HEADER)
        menu_screen.blit(font.render("Select Difficulty:", True, WHITE), (50, 40))
        menu_screen.blit(small_font.render("1: Easy  |  2: Medium  |  3: Hard", True, WHITE), (50, 120))
        menu_screen.blit(small_font.render("Press ESC to Quit", True, WHITE), (50, 200)) # Added visual hint
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit()
                exit() # Force exit the script immediately
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: # Added Escape key support
                    pygame.quit()
                    exit()
                if e.unicode in DIFFICULTIES:
                    diff = DIFFICULTIES[e.unicode]

    # Setup Board based on difficulty
    ROWS, COLS, MINE_COUNT, TILE_SIZE = diff
    WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE
    screen = pygame.display.set_mode((WIDTH, HEIGHT + HEADER_H))
    
    # Reset game state
    board = [[Cell(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]
    particles, floating_texts = [], []
    first_click = True
    game_over = won = False
    score = shake = 0
    exit_rect = pygame.Rect(WIDTH - 45, 15, 30, 30)
    clock = pygame.time.Clock()

    while True:
        screen.fill(COLOR_HEADER)
        
        # Shake logic
        ox = random.randint(-shake, shake) if shake > 0 else 0
        oy = random.randint(-shake, shake) if shake > 0 else 0
        if shake > 0: shake -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if exit_rect.collidepoint((mx, my)): pygame.quit(); return
                
                if not game_over and my >= HEADER_H:
                    c, r = mx // TILE_SIZE, (my - HEADER_H) // TILE_SIZE
                    if event.button == 1: # Left Click
                        if first_click:
                            setup_mines(board, ROWS, COLS, MINE_COUNT, r, c)
                            first_click = False
                        
                        if not board[r][c].flagged and not board[r][c].revealed:
                            if board[r][c].mine:
                                game_over, shake = True, 20
                                for row in board: 
                                    for cl in row: 
                                        if cl.mine: cl.revealed = True
                            else:
                                revealed = iterative_reveal(board, r, c, ROWS, COLS)
                                score += revealed * 10
                                floating_texts.append(FloatingText(mx, my, f"+{revealed*10}"))
                                for _ in range(5): 
                                    particles.append(Particle(mx, my, COLOR_GRASS_L))
                    
                    elif event.button == 3: # Right Click
                        if not board[r][c].revealed:
                            board[r][c].flagged = not board[r][c].flagged

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main_game() # Restart to menu
                return

        # Draw Board
        for row in board:
            for cell in row: cell.draw(screen, ox, oy)
        
        # Update and Draw Effects
        for p in particles[:]: 
            if p.update(): p.draw(screen)
            else: particles.remove(p)
            
        for ft in floating_texts[:]:
            if ft.update():
                t = small_font.render(ft.text, True, WHITE)
                t.set_alpha(ft.life)
                screen.blit(t, (ft.x, ft.y))
            else: floating_texts.remove(ft)

        # UI Header elements
        pygame.draw.rect(screen, EXIT_RED, exit_rect, border_radius=5)
        screen.blit(small_font.render("X", True, WHITE), (WIDTH-35, 20))
        screen.blit(font.render(f"SCORE: {score}", True, WHITE), (20, 20))
        
        # Check Win Condition
        if not game_over:
            unrev = sum(1 for r_idx in board for c_obj in r_idx if not c_obj.revealed and not c_obj.mine)
            if unrev == 0: 
                game_over = won = True
                score += 1000

        if game_over:
            msg = "VICTORY! (+1000)" if won else "GAME OVER (Press R)"
            color = GOLD if won else WHITE
            screen.blit(small_font.render(msg, True, color), (20, 60))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_game()