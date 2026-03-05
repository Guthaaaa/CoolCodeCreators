import pygame
import random

# Initialize Pygame
pygame.init()

# Settings
WIDTH, HEIGHT = 600, 600
HEADER_H = 80
ROWS, COLS = 10, 10
SQUARE_SIZE = WIDTH // COLS
MINE_COUNT = 15

# Colors
COLOR_GRASS_L = (170, 215, 81)
COLOR_GRASS_D = (162, 209, 73)
COLOR_HEADER = (74, 117, 44)
COLOR_REVEAL_L = (229, 194, 159)
COLOR_REVEAL_D = (215, 184, 153)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

NUM_COLORS = {
    1: (25, 118, 210), 2: (56, 142, 60), 3: (211, 47, 47),
    4: (123, 31, 162), 5: (255, 143, 0), 6: (0, 151, 167)
}

screen = pygame.display.set_mode((WIDTH, HEIGHT + HEADER_H))
pygame.display.set_caption("Google-Style Minesweeper")
font = pygame.font.SysFont("arial", 30, bold=True)
small_font = pygame.font.SysFont("arial", 20, bold=True)

class Cell:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.mine = False
        self.revealed = False
        self.flagged = False
        self.adj_mines = 0

    def draw(self):
        x, y = self.c * SQUARE_SIZE, self.r * SQUARE_SIZE + HEADER_H
        is_dark = (self.r + self.c) % 2 == 1
        
        if not self.revealed:
            color = COLOR_GRASS_D if is_dark else COLOR_GRASS_L
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            if self.flagged:
                pygame.draw.circle(screen, (231, 71, 29), (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2), 10)
        else:
            color = COLOR_REVEAL_D if is_dark else COLOR_REVEAL_L
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            if self.mine:
                pygame.draw.circle(screen, BLACK, (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2), 15)
            elif self.adj_mines > 0:
                txt = font.render(str(self.adj_mines), True, NUM_COLORS.get(self.adj_mines, BLACK))
                screen.blit(txt, (x + 22, y + 12))

def create_board():
    board = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
    mines = 0
    while mines < MINE_COUNT:
        r, c = random.randint(0, ROWS-1), random.randint(0, COLS-1)
        if not board[r][c].mine:
            board[r][c].mine = True
            mines += 1
    
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c].mine: continue
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc].mine:
                        board[r][c].adj_mines += 1
    return board

def flood_fill(board, r, c):
    if not (0 <= r < ROWS and 0 <= c < COLS) or board[r][c].revealed or board[r][c].flagged:
        return
    board[r][c].revealed = True
    if board[r][c].adj_mines == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                flood_fill(board, r + dr, c + dc)

def main():
    # --- INITIALIZE STATE ---
    board = create_board()
    game_over = False
    won = False

    while True:
        screen.fill(COLOR_HEADER)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            # Restart Logic
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = create_board()
                    game_over = False
                    won = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mx, my = pygame.mouse.get_pos()
                if my < HEADER_H: continue
                c, r = mx // SQUARE_SIZE, (my - HEADER_H) // SQUARE_SIZE
                cell = board[r][c]
                
                if event.button == 1: # Left Click
                    if not cell.flagged:
                        if cell.mine:
                            game_over = True
                            for row in board: 
                                for cl in row: 
                                    if cl.mine: cl.revealed = True
                        else:
                            flood_fill(board, r, c)
                elif event.button == 3: # Right Click
                    cell.flagged = not cell.flagged

        # Drawing
        for row in board:
            for cell in row:
                cell.draw()
        
        # Header UI
        status = "MINESWEEPER"
        if game_over: status = "YOU WIN!" if won else "GAME OVER"
        txt = font.render(status, True, WHITE)
        screen.blit(txt, (20, 20))
        
        retry_txt = small_font.render("Press 'R' to Restart", True, WHITE)
        screen.blit(retry_txt, (WIDTH - 180, 30))

        # Check Win
        unrevealed = sum(1 for r in board for c in r if not c.revealed and not c.mine)
        if unrevealed == 0 and not game_over:
            game_over = True
            won = True

        pygame.display.flip()

if __name__ == "__main__":
    main()