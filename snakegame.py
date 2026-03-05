import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Get screen resolution
info = pygame.display.Info()
SCREEN_W = info.current_w
SCREEN_H = info.current_h

# --- SETTINGS ---
BLOCK_SIZE = 60  
HEADER_HEIGHT = 90 
APPLES_PER_SPAWN = 4

# Colors
COLOR_GRASS_LIGHT = (170, 215, 81)
COLOR_GRASS_DARK = (162, 209, 73)
COLOR_SCORE_BAR = (74, 117, 44)
COLOR_SNAKE = (70, 115, 232)
COLOR_APPLE = (231, 71, 29)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption('Google Snake: Restart Edition')
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 48, bold=True)
large_font = pygame.font.SysFont("arial", 80, bold=True)

# Grid Calculations
TOTAL_COLS = SCREEN_W // BLOCK_SIZE
TOTAL_ROWS = (SCREEN_H - HEADER_HEIGHT) // BLOCK_SIZE
MAX_SQUARES = TOTAL_COLS * TOTAL_ROWS

def draw_background():
    pygame.draw.rect(screen, COLOR_SCORE_BAR, [0, 0, SCREEN_W, HEADER_HEIGHT])
    for row in range(TOTAL_ROWS):
        for col in range(TOTAL_COLS):
            color = COLOR_GRASS_LIGHT if (row + col) % 2 == 0 else COLOR_GRASS_DARK
            pygame.draw.rect(screen, color, [col * BLOCK_SIZE, row * BLOCK_SIZE + HEADER_HEIGHT, BLOCK_SIZE, BLOCK_SIZE])

def draw_eyes(head_x, head_y, dx, dy):
    eye_size = 6
    # Determine eye direction based on movement
    if dx > 0: left, right = (45, 15), (45, 45)
    elif dx < 0: left, right = (15, 15), (15, 45)
    elif dy < 0: left, right = (15, 15), (45, 15)
    else: left, right = (15, 45), (45, 45) 

    for pos in [left, right]:
        pygame.draw.circle(screen, WHITE, (head_x + pos[0], head_y + pos[1]), eye_size + 2)
        pygame.draw.circle(screen, BLACK, (head_x + pos[0], head_y + pos[1]), eye_size)

def spawn_multiple_apples(snake_body, snake_len):
    new_apples = []
    space_left = MAX_SQUARES - snake_len
    to_spawn = min(APPLES_PER_SPAWN, space_left)
    
    while len(new_apples) < to_spawn:
        fx = random.randint(0, TOTAL_COLS - 1) * BLOCK_SIZE
        fy = random.randint(0, TOTAL_ROWS - 1) * BLOCK_SIZE + HEADER_HEIGHT
        if [fx, fy] not in snake_body and [fx, fy] not in new_apples:
            new_apples.append([fx, fy])
    return new_apples

def game_loop():
    while True: # Main application loop to allow multiple games
        # --- RESET GAME STATE ---
        x = (SCREEN_W // 2 // BLOCK_SIZE) * BLOCK_SIZE
        y = ((SCREEN_H // 2 - HEADER_HEIGHT) // BLOCK_SIZE) * BLOCK_SIZE + HEADER_HEIGHT
        dx, dy = 0, 0
        snake_body = [[x, y]]
        snake_len = 1
        score = 0
        apples = spawn_multiple_apples(snake_body, snake_len)
        game_active = True
        won = False

        # --- INDIVIDUAL MATCH LOOP ---
        while game_active:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: pygame.quit(); exit()
                    if event.key == pygame.K_LEFT and dx == 0: dx, dy = -BLOCK_SIZE, 0
                    elif event.key == pygame.K_RIGHT and dx == 0: dx, dy = BLOCK_SIZE, 0
                    elif event.key == pygame.K_UP and dy == 0: dx, dy = 0, -BLOCK_SIZE
                    elif event.key == pygame.K_DOWN and dy == 0: dx, dy = 0, BLOCK_SIZE

            x += dx
            y += dy

            # Check Win
            if snake_len >= MAX_SQUARES:
                won = True
                game_active = False

            # Collision Logic
            if x < 0 or x >= SCREEN_W or y < HEADER_HEIGHT or y >= SCREEN_H or [x, y] in snake_body[:-1]:
                game_active = False

            head = [x, y]
            snake_body.append(head)
            if len(snake_body) > snake_len: del snake_body[0]

            # Render
            draw_background()
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (40, 20))

            for apple in apples:
                pygame.draw.circle(screen, COLOR_APPLE, (apple[0] + BLOCK_SIZE//2, apple[1] + BLOCK_SIZE//2), BLOCK_SIZE//2 - 5)

            for part in snake_body:
                pygame.draw.rect(screen, COLOR_SNAKE, [part[0], part[1], BLOCK_SIZE, BLOCK_SIZE], border_radius=8)
            
            draw_eyes(snake_body[-1][0], snake_body[-1][1], dx, dy)

            # Eat Apple
            if [x, y] in apples:
                score += 1
                snake_len += 1
                apples = spawn_multiple_apples(snake_body, snake_len)

            pygame.display.update()
            clock.tick(10)

        # --- GAME OVER / RESTART SCREEN ---
        waiting_for_input = True
        while waiting_for_input:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))

            msg = "🏆 YOU WIN! 🏆" if won else "GAME OVER"
            color = GOLD if won else WHITE
            
            main_txt = large_font.render(msg, True, color)
            sub_txt = font.render("Press 'R' to Restart or 'ESC' to Quit", True, WHITE)
            
            screen.blit(main_txt, (SCREEN_W//2 - main_txt.get_width()//2, SCREEN_H//2 - 100))
            screen.blit(sub_txt, (SCREEN_W//2 - sub_txt.get_width()//2, SCREEN_H//2 + 20))
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting_for_input = False # Break this loop to restart game_loop
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); exit()

if __name__ == "__main__":
    game_loop()