import sys
import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Get screen resolution
info = pygame.display.Info()
SCREEN_W, SCREEN_H = info.current_w, info.current_h
BLOCK_SIZE = 60  
HEADER_HEIGHT = 100 # Slightly taller for better UI

# --- COLORS ---
COLOR_GRASS_L = (170, 215, 81)
COLOR_GRASS_D = (162, 209, 73)
COLOR_SCORE_BAR = (74, 117, 44)
WHITE, BLACK, RED, GOLD = (255, 255, 255), (0, 0, 0), (231, 71, 29), (255, 215, 0)
SILVER, BRONZE, CYAN = (192, 192, 192), (205, 127, 50), (0, 255, 255)

SKINS = {
    "BLUE": (70, 115, 232),
    "NEON": (57, 255, 20),
    "GOLD": (218, 165, 32),
    "PURPLE": (147, 0, 211)
}

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32, bold=True)
small_font = pygame.font.SysFont("arial", 20, bold=True)
title_font = pygame.font.SysFont("arial", 80, bold=True)
mid_font = pygame.font.SysFont("arial", 50, bold=True)

high_score = 0

def get_rank_info(score):
    if score >= 100: return "SNAKE GOD", CYAN, 100, 100
    if score >= 50:  return "ELITE", GOLD, 50, 100
    if score >= 30:  return "PRO", SILVER, 30, 50
    if score >= 10:  return "AMATEUR", BRONZE, 10, 30
    return "NEWBIE", WHITE, 0, 10

def draw_header(score, skin_name, offset):
    # Draw Background Bar
    pygame.draw.rect(screen, COLOR_SCORE_BAR, [offset[0], offset[1], SCREEN_W, HEADER_HEIGHT])
    
    # 1. Left Side: Current Score & Skin
    pygame.draw.circle(screen, RED, (40 + offset[0], 50 + offset[1]), 15)
    score_txt = font.render(f"{score}", True, WHITE)
    screen.blit(score_txt, (65 + offset[0], 32 + offset[1]))
    skin_txt = small_font.render(f"SKIN: {skin_name}", True, WHITE)
    screen.blit(skin_txt, (40 + offset[0], 70 + offset[1]))

    # 2. Middle: Progress Bar & Rank
    rank_name, rank_color, current_min, next_goal = get_rank_info(score)
    bar_w, bar_h = 300, 20
    bar_x = (SCREEN_W // 2) - (bar_w // 2) + offset[0]
    bar_y = 55 + offset[1]
    
    # Draw Progress Bar Background
    pygame.draw.rect(screen, (50, 80, 30), [bar_x, bar_y, bar_w, bar_h], border_radius=10)
    # Draw Fill
    progress = min((score - current_min) / (next_goal - current_min), 1.0)
    pygame.draw.rect(screen, rank_color, [bar_x, bar_y, int(bar_w * progress), bar_h], border_radius=10)
    
    rank_label = small_font.render(f"RANK: {rank_name}", True, rank_color)
    screen.blit(rank_label, (bar_x, 25 + offset[1]))
    goal_txt = small_font.render(f"{score}/{next_goal}", True, WHITE)
    screen.blit(goal_txt, (bar_x + bar_w - goal_txt.get_width(), 25 + offset[1]))

    # 3. Right Side: High Score
    tx, ty = SCREEN_W - 180 + offset[0], 40 + offset[1]
    pygame.draw.rect(screen, GOLD, [tx, ty, 25, 15], border_radius=3)
    pygame.draw.rect(screen, GOLD, [tx + 10, ty + 15, 5, 8])
    pygame.draw.rect(screen, GOLD, [tx + 5, ty + 23, 15, 4], border_radius=2)
    best_txt = font.render(f"{high_score}", True, WHITE)
    screen.blit(best_txt, (tx + 35, 32 + offset[1]))
    label_best = small_font.render("BEST", True, GOLD)
    screen.blit(label_best, (tx, 70 + offset[1]))

def draw_background(offset=(0,0)):
    # Grid area starts after header
    for row in range((SCREEN_H - HEADER_HEIGHT) // BLOCK_SIZE + 1):
        for col in range(SCREEN_W // BLOCK_SIZE + 1):
            color = COLOR_GRASS_L if (row + col) % 2 == 0 else COLOR_GRASS_D
            pygame.draw.rect(screen, color, [col * BLOCK_SIZE + offset[0], row * BLOCK_SIZE + HEADER_HEIGHT + offset[1], BLOCK_SIZE, BLOCK_SIZE])

def draw_snake_face(head_x, head_y, dx, dy, offset):
    eye_size = 7
    if dx > 0: l, r = (38, 18), (38, 42)
    elif dx < 0: l, r = (22, 18), (22, 42)
    elif dy < 0: l, r = (18, 22), (42, 22)
    else: l, r = (18, 38), (42, 38)
    for pos in [l, r]:
        pygame.draw.circle(screen, WHITE, (head_x + pos[0] + offset[0], head_y + pos[1] + offset[1]), eye_size + 2)
        pygame.draw.circle(screen, BLACK, (head_x + pos[0] + offset[0], head_y + pos[1] + offset[1]), eye_size)

def show_summary(final_score):
    rank_name, rank_color, _, _ = get_rank_info(final_score)
    while True:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.set_alpha(200)
        overlay.fill((10, 25, 10))
        screen.blit(overlay, (0,0))
        cx = SCREEN_W // 2
        screen.blit(title_font.render("GAME OVER", True, WHITE), (cx - 200, 100))
        screen.blit(mid_font.render(f"Score: {final_score}", True, WHITE), (cx - 100, 220))
        screen.blit(font.render("RANK ACHIEVED:", True, WHITE), (cx - 120, 320))
        screen.blit(title_font.render(rank_name, True, rank_color), (cx - (title_font.size(rank_name)[0]//2), 380))
        screen.blit(font.render(f"Global Best: {high_score}", True, GOLD), (cx - 120, 520))
        screen.blit(font.render("R: Restart | M: Menu | ESC: Quit", True, SILVER), (cx - 240, SCREEN_H - 100))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "RESTART"
                if event.key == pygame.K_m: return "MENU"
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

def skin_menu():
    selected_index = 0
    skin_names = list(SKINS.keys())
    while True:
        screen.fill(COLOR_SCORE_BAR)
        screen.blit(title_font.render("CHOOSE YOUR SKIN", True, WHITE), (SCREEN_W // 2 - 350, 150))
        for i, name in enumerate(skin_names):
            rect_y = 300 + (i * 80)
            if i == selected_index:
                pygame.draw.rect(screen, WHITE, [SCREEN_W // 2 - 160, rect_y - 10, 320, 70], border_radius=20)
            pygame.draw.rect(screen, SKINS[name], [SCREEN_W // 2 - 150, rect_y, 300, 50], border_radius=15)
            screen.blit(font.render(name, True, BLACK if i == selected_index else WHITE), (SCREEN_W // 2 - 50, rect_y + 5))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(skin_names)
                if event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(skin_names)
                if event.key == pygame.K_RETURN: return skin_names[selected_index]
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

def game_loop(skin_name):
    global high_score
    skin_color = SKINS[skin_name]
    x, y = (SCREEN_W // 2 // BLOCK_SIZE) * BLOCK_SIZE, ((SCREEN_H // 2 - HEADER_HEIGHT) // BLOCK_SIZE) * BLOCK_SIZE + HEADER_HEIGHT
    dx, dy = 0, 0
    snake_body, snake_len = [[x, y]], 1
    score, shake_frames = 0, 0
    
    def spawn_apples():
        apples = []
        for _ in range(4):
            ax = random.randint(0, (SCREEN_W // BLOCK_SIZE) - 1) * BLOCK_SIZE
            ay = random.randint(0, ((SCREEN_H - HEADER_HEIGHT) // BLOCK_SIZE) - 1) * BLOCK_SIZE + HEADER_HEIGHT
            apples.append([ax, ay])
        return apples

    apples = spawn_apples()

    while True:
        offset = (random.randint(-4, 4), random.randint(-4, 4)) if shake_frames > 0 else (0,0)
        if shake_frames > 0: shake_frames -= 1

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "QUIT"
                if event.key == pygame.K_LEFT and dx == 0: dx, dy = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0: dx, dy = BLOCK_SIZE, 0
                elif event.key == pygame.K_UP and dy == 0: dx, dy = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and dy == 0: dx, dy = 0, BLOCK_SIZE

        x, y = x + dx, y + dy
        if x < 0 or x >= SCREEN_W or y < HEADER_HEIGHT or y >= SCREEN_H or [x, y] in snake_body[:-1]:
            if score > high_score: high_score = score
            return score

        snake_body.append([x, y])
        if len(snake_body) > snake_len: del snake_body[0]

        draw_background(offset)
        draw_header(score, skin_name, offset)
        
        for apple in apples:
            pygame.draw.circle(screen, (150, 0, 0), (apple[0]+30+offset[0], apple[1]+30+offset[1]), 30)
            pygame.draw.circle(screen, RED, (apple[0]+30+offset[0], apple[1]+30+offset[1]), 25)
        
        for i, part in enumerate(snake_body):
            pygame.draw.rect(screen, skin_color, [part[0]+offset[0], part[1]+offset[1], BLOCK_SIZE, BLOCK_SIZE], border_radius=20)
            if i > 0:
                prev = snake_body[i-1]
                mid_x, mid_y = (part[0] + prev[0]) // 2, (part[1] + prev[1]) // 2
                pygame.draw.rect(screen, skin_color, [mid_x+offset[0], mid_y+offset[1], BLOCK_SIZE, BLOCK_SIZE], border_radius=5)
        
        draw_snake_face(snake_body[-1][0], snake_body[-1][1], dx, dy, offset)

        if [x, y] in apples:
            score, snake_len, shake_frames, apples = score + 1, snake_len + 1, 5, spawn_apples()

        pygame.display.update()
        clock.tick(8.5)

# --- EXECUTION ---
current_skin = skin_menu()
while True:
    result = game_loop(current_skin)
    if isinstance(result, int):
        choice = show_summary(result)
        if choice == "MENU": current_skin = skin_menu()
    else: break