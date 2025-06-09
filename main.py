import pygame
import random
import sys
import time
import math
import json
import os
from enum import Enum
pygame.init()
pygame.mixer.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Minecraft Snake')
DIRT_BROWN = (92, 60, 17)
GRASS_GREEN = (92, 156, 48)
STONE_GRAY = (162, 162, 162)
WOOD_BROWN = (143, 86, 59)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
snake_block = 16  
snake_speed = 15
food_block = 16
clock = pygame.time.Clock()
try:
    title_font = pygame.font.Font('Minecraft.ttf', 72)
    menu_font = pygame.font.Font('Minecraft.ttf', 36)
    game_font = pygame.font.Font('Minecraft.ttf', 24)
    score_font = pygame.font.Font('Minecraft.ttf', 32)
    input_font = pygame.font.Font('Minecraft.ttf', 28)
except:
    title_font = pygame.font.SysFont('arial', 72, bold=True)
    menu_font = pygame.font.SysFont('arial', 36)
    game_font = pygame.font.SysFont('arial', 24)
    score_font = pygame.font.SysFont('arial', 32, bold=True)
    input_font = pygame.font.SysFont('arial', 28)
try:
    pygame.mixer.music.load('sound.mp3')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    makan_sound = pygame.mixer.Sound('food.mp3')
    gerakan_sound = pygame.mixer.Sound('wosh.mp3')
    game_over_sound = pygame.mixer.Sound('game_over.mp3')
    click_sound = pygame.mixer.Sound('food.mp3')
except:
    class DummySound:
        def play(self): pass
    makan_sound = gerakan_sound = game_over_sound = click_sound = DummySound()
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_SELECT = 3
    AREA_SELECT = 4
    NAME_INPUT = 5
    LEADERBOARD = 6
    MULTIPLAYER_SETUP = 7
game_state = GameState.MENU
class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
difficulty = Difficulty.MEDIUM
class GameMode(Enum):
    SINGLE = 0
    MULTIPLAYER = 1
game_mode = GameMode.SINGLE
class GameArea:
    def __init__(self, name, walls, bg_color, wall_color):
        self.name = name
        self.walls = walls 
        self.bg_color = bg_color
        self.wall_color = wall_color
AREAS = [
    GameArea("Grasslands", [], GRASS_GREEN, DIRT_BROWN),
    GameArea("Stone Box", [
        (100, 100, 600, 20),
        (100, 100, 20, 400),
        (100, 480, 600, 20),
        (680, 100, 20, 400)
    ], STONE_GRAY, STONE_GRAY),
    GameArea("Nether Maze", [
        (200, 0, 20, 300),
        (400, 300, 20, 300),
        (600, 0, 20, 200),
        (0, 200, 200, 20),
        (300, 400, 200, 20),
        (500, 100, 200, 20)
    ], (100, 0, 0), (150, 50, 50)), 
    GameArea("Wood Chambers", [
        (0, 150, 300, 20),
        (500, 150, 300, 20),
        (0, 450, 300, 20),
        (500, 450, 300, 20),
        (150, 150, 20, 300),
        (650, 150, 20, 300)
    ], WOOD_BROWN, (100, 60, 30))
]
current_area = AREAS[0]
class Snake:
    def __init__(self, x, y, color, controls):
        self.snake_list = [[x, y]]
        self.snake_length = 1
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.color = color
        self.controls = controls  
        self.alive = True
        self.score = 0
player1 = Snake(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, GRASS_GREEN, 
                {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN})
player2 = Snake(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, BLUE, 
                {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s})
snakes = [player1]
food_x = random.randrange(0, SCREEN_WIDTH - food_block, food_block)
food_y = random.randrange(0, SCREEN_HEIGHT - food_block, food_block)
food_type = random.choice(["apple", "berry", "steak"])  
enemies = []
ENEMY_TYPES = [
    {"name": "Zombie", "color": (50, 100, 50), "speed": 1},
    {"name": "Skeleton", "color": (200, 200, 200), "speed": 2},
    {"name": "Creeper", "color": (50, 200, 50), "speed": 3}
]
enemy_size = snake_block
last_enemy_spawn = 0
enemy_spawn_interval = 5000  
high_score = 0
player_name = ""
leaderboard = []
def load_leaderboard():
    global leaderboard
    try:
        if os.path.exists('leaderboard.json'):
            with open('leaderboard.json', 'r') as f:
                leaderboard = json.load(f)
    except:
        leaderboard = []
def save_leaderboard():
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)
load_leaderboard()
title_y = -100
menu_option = 0
buttons = []
button_anim = 0
game_over_alpha = 0
pulse_anim = 0
name_input_active = True
multiplayer_option = 0
def create_buttons():
    global buttons
    buttons = []
    button_texts = ["START GAME", "DIFFICULTY", "GAME AREA", "LEADERBOARD", "MULTIPLAYER", "QUIT"]
    for i, text in enumerate(button_texts):
        text_surf = menu_font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 250 + i*60))
        buttons.append({
            "text": text_surf,
            "rect": text_rect,
            "color": WOOD_BROWN
        })
create_buttons()
def create_multiplayer_buttons():
    mp_buttons = []
    button_texts = ["1 PLAYER", "2 PLAYERS", "START GAME", "BACK"]
    for i, text in enumerate(button_texts):
        text_surf = menu_font.render(text, True, WHITE)
        y_pos = 200 if i < 2 else (350 if i == 2 else 450)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y_pos))
        mp_buttons.append({
            "text": text_surf,
            "rect": text_rect,
            "color": STONE_GRAY
        })
    return mp_buttons

multiplayer_buttons = create_multiplayer_buttons()
def create_difficulty_buttons():
    diff_buttons = []
    button_texts = ["EASY", "MEDIUM", "HARD"]
    for i, text in enumerate(button_texts):
        text_surf = menu_font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 250 + i*100))
        diff_buttons.append({
            "text": text_surf,
            "rect": text_rect,
            "color": STONE_GRAY
        })
    return diff_buttons

difficulty_buttons = create_difficulty_buttons()
def create_area_buttons():
    area_buttons = []
    for i, area in enumerate(AREAS):
        text_surf = menu_font.render(area.name, True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 200 + i*90))
        area_buttons.append({
            "text": text_surf,
            "rect": text_rect,
            "color": area.wall_color
        })
    return area_buttons
area_buttons = create_area_buttons()
def draw_minecraft_button(surface, rect, color, text="", text_color=WHITE):
    pygame.draw.rect(surface, color, rect)
    highlight_color = (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50))
    pygame.draw.line(surface, highlight_color, rect.topleft, rect.topright, 3)
    pygame.draw.line(surface, highlight_color, rect.topleft, rect.bottomleft, 3)
    shadow_color = (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50))
    pygame.draw.line(surface, shadow_color, rect.bottomleft, rect.bottomright, 3)
    pygame.draw.line(surface, shadow_color, rect.topright, rect.bottomright, 3)
    if text:
        text_surf = menu_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)
def draw_snake(snake_list, color, is_head=True):
    for i, block in enumerate(snake_list):
        pygame.draw.rect(screen, DIRT_BROWN, (block[0], block[1], snake_block, snake_block))
        pygame.draw.rect(screen, (max(0, DIRT_BROWN[0]-20), max(0, DIRT_BROWN[1]-20), max(0, DIRT_BROWN[2]-20)), 
                         (block[0], block[1], snake_block, snake_block), 1)
        if is_head and i == len(snake_list) - 1:
            pygame.draw.rect(screen, color, (block[0], block[1], snake_block, snake_block))
            pygame.draw.rect(screen, (max(0, color[0]-20), max(0, color[1]-20), max(0, color[2]-20)), 
                             (block[0], block[1], snake_block, snake_block), 1)
            head_center_x = block[0] + snake_block // 2
            head_center_y = block[1] + snake_block // 2
            eye_offset_x = 0
            eye_offset_y = 0
            if len(snakes) > 0:
                dx = snakes[0].dx
                dy = snakes[0].dy
                if dx > 0:  # Moving right
                    eye_offset_x = 3
                elif dx < 0:  # Moving left
                    eye_offset_x = -3
                elif dy > 0:  # Moving down
                    eye_offset_y = 3
                elif dy < 0:  # Moving up
                    eye_offset_y = -3
            pygame.draw.rect(screen, BLACK, (head_center_x - 4 + eye_offset_x, head_center_y - 2, 3, 3))
            pygame.draw.rect(screen, BLACK, (head_center_x + 1 + eye_offset_x, head_center_y - 2, 3, 3))
            pygame.draw.rect(screen, WHITE, (head_center_x - 3 + eye_offset_x, head_center_y - 1, 1, 1))
            pygame.draw.rect(screen, WHITE, (head_center_x + 2 + eye_offset_x, head_center_y - 1, 1, 1))
def draw_food(x, y, pulse, food_type):
    size = food_block + int(pulse * 3)
    offset = (food_block - size) // 2
    if food_type == "apple":
        pygame.draw.rect(screen, RED, (x + offset, y + offset, size, size))
        pygame.draw.rect(screen, (100, 70, 0), (x + offset + size//2 - 1, y + offset - 3, 2, 3))
    elif food_type == "berry":
        pygame.draw.rect(screen, (200, 0, 200), (x + offset, y + offset, size, size))
    elif food_type == "steak":
        pygame.draw.rect(screen, (150, 100, 50), (x + offset, y + offset, size, size))
    
    pygame.draw.rect(screen, BLACK, (x + offset, y + offset, size, size), 1)
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_TYPES[enemy['type']]['color'], 
                         (enemy['x'], enemy['y'], enemy_size, enemy_size))
        pygame.draw.rect(screen, BLACK, (enemy['x'] + 4, enemy['y'] + 4, 3, 3))
        pygame.draw.rect(screen, BLACK, (enemy['x'] + enemy_size - 7, enemy['y'] + 4, 3, 3))
        name_text = game_font.render(ENEMY_TYPES[enemy['type']]['name'], True, WHITE)
        screen.blit(name_text, (enemy['x'] - (name_text.get_width() - enemy_size) // 2, enemy['y'] - 20))
def draw_walls():
    for wall in current_area.walls:
        wall_rect = pygame.Rect(wall)
        pygame.draw.rect(screen, current_area.wall_color, wall_rect)
        for x in range(wall_rect.left, wall_rect.right, 4):
            pygame.draw.line(screen, (max(0, current_area.wall_color[0]-20), 
                            max(0, current_area.wall_color[1]-20), 
                            max(0, current_area.wall_color[2]-20)), 
                            (x, wall_rect.top), (x, wall_rect.bottom), 1)
        for y in range(wall_rect.top, wall_rect.bottom, 4):
            pygame.draw.line(screen, (max(0, current_area.wall_color[0]-20), 
                            max(0, current_area.wall_color[1]-20), 
                            max(0, current_area.wall_color[2]-20)), 
                            (wall_rect.left, y), (wall_rect.right, y), 1)
        pygame.draw.line(screen, (min(255, current_area.wall_color[0]+30), 
                         min(255, current_area.wall_color[1]+30), 
                         min(255, current_area.wall_color[2]+30)), 
                         wall_rect.topleft, wall_rect.topright, 2)
        pygame.draw.line(screen, (min(255, current_area.wall_color[0]+30), 
                         min(255, current_area.wall_color[1]+30), 
                         min(255, current_area.wall_color[2]+30)), 
                         wall_rect.topleft, wall_rect.bottomleft, 2)
        
        pygame.draw.line(screen, (max(0, current_area.wall_color[0]-30), 
                         max(0, current_area.wall_color[1]-30), 
                         max(0, current_area.wall_color[2]-30)), 
                         wall_rect.bottomleft, wall_rect.bottomright, 2)
        pygame.draw.line(screen, (max(0, current_area.wall_color[0]-30), 
                         max(0, current_area.wall_color[1]-30), 
                         max(0, current_area.wall_color[2]-30)), 
                         wall_rect.topright, wall_rect.bottomright, 2)
def draw_background():
    screen.fill(current_area.bg_color)
    for x in range(0, SCREEN_WIDTH, 32):
        pygame.draw.line(screen, (max(0, current_area.bg_color[0]-10), 
                         max(0, current_area.bg_color[1]-10), 
                         max(0, current_area.bg_color[2]-10)), 
                         (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, 32):
        pygame.draw.line(screen, (max(0, current_area.bg_color[0]-10), 
                         max(0, current_area.bg_color[1]-10), 
                         max(0, current_area.bg_color[2]-10)), 
                         (0, y), (SCREEN_WIDTH, y), 1)
def draw_menu():
    global title_y, button_anim, pulse_anim
    screen.fill(DIRT_BROWN)
    pygame.draw.rect(screen, GRASS_GREEN, (0, 0, SCREEN_WIDTH, 60))
    pygame.draw.rect(screen, STONE_GRAY, (0, SCREEN_HEIGHT-40, SCREEN_WIDTH, 40))
    if title_y < 100:
        title_y += 5
    title_text = title_font.render("MINECRAFT SNAKE", True, GOLD)
    title_shadow = title_font.render("MINECRAFT SNAKE", True, (100, 80, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2 + 3, title_y + 3))
    screen.blit(title_shadow, title_rect)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, title_y))
    screen.blit(title_text, title_rect)
    for i, button in enumerate(buttons):
        is_selected = i == menu_option
        button_rect = pygame.Rect(
            button["rect"].x - 40,  # Increased left padding
            button["rect"].y - 10 + (i * 20),  # Added vertical spacing between buttons
            button["rect"].width + 80,  # Increased total width
            button["rect"].height + 20
        )
        radius = 15
        points = [
            (button_rect.left + radius, button_rect.top),
            (button_rect.right - radius, button_rect.top),
            (button_rect.right, button_rect.top + radius),
            (button_rect.right, button_rect.bottom - radius),
            (button_rect.right - radius, button_rect.bottom),
            (button_rect.left + radius, button_rect.bottom),
            (button_rect.left, button_rect.bottom - radius),
            (button_rect.left, button_rect.top + radius),
        ]
        pygame.draw.polygon(screen, button["color"] if not is_selected else (
            min(255, button["color"][0]+30),
            min(255, button["color"][1]+30),
            min(255, button["color"][2]+30)
        ), points)
        pygame.draw.circle(screen, button["color"] if not is_selected else (
            min(255, button["color"][0]+30),
            min(255, button["color"][1]+30),
            min(255, button["color"][2]+30)
        ), (button_rect.left + radius, button_rect.top + radius), radius)
        pygame.draw.circle(screen, button["color"] if not is_selected else (
            min(255, button["color"][0]+30),
            min(255, button["color"][1]+30),
            min(255, button["color"][2]+30)
        ), (button_rect.right - radius, button_rect.top + radius), radius)
        pygame.draw.circle(screen, button["color"] if not is_selected else (
            min(255, button["color"][0]+30),
            min(255, button["color"][1]+30),
            min(255, button["color"][2]+30)
        ), (button_rect.left + radius, button_rect.bottom - radius), radius)
        pygame.draw.circle(screen, button["color"] if not is_selected else (
            min(255, button["color"][0]+30),
            min(255, button["color"][1]+30),
            min(255, button["color"][2]+30)
        ), (button_rect.right - radius, button_rect.bottom - radius), radius)
        desc_text = ""
        if i == 0:  # START GAME
            desc_text = "Begin your adventure!"
        elif i == 1:  # DIFFICULTY
            desc_text = "Choose your challenge level"
        elif i == 2:  # GAME AREA
            desc_text = "Select your playing field"
        elif i == 3:  # LEADERBOARD
            desc_text = "View high scores"
        elif i == 4:  # MULTIPLAYER
            desc_text = "Play with a friend"
        elif i == 5:  # QUIT
            desc_text = "Exit the game"
        desc_surface = game_font.render(desc_text, True, (200, 200, 200))
        desc_rect = desc_surface.get_rect(right=button_rect.left - 10, centery=button_rect.centery)
        screen.blit(desc_surface, desc_rect)
        draw_minecraft_button(
            screen,
            button_rect,
            button["color"] if not is_selected else (min(255, button["color"][0]+30), 
                                          min(255, button["color"][1]+30), 
                                          min(255, button["color"][2]+30)),
            button["text"].get_text() if hasattr(button["text"], 'get_text') else "",
            WHITE
        )
    version_text = game_font.render("Games Snake By Dwi Bakti N Dev v1.0", True, WHITE)
    screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, 
                               SCREEN_HEIGHT - version_text.get_height() - 10))
def draw_multiplayer_setup():
    screen.fill(DIRT_BROWN)
    title_text = title_font.render("MULTIPLAYER SETUP", True, GOLD)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    desc_text = game_font.render("Choose your game mode and start playing with friends!", True, WHITE)
    desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, 180))
    screen.blit(desc_text, desc_rect)
    count_text = menu_font.render("SELECT PLAYER COUNT:", True, WHITE)
    count_rect = count_text.get_rect(center=(SCREEN_WIDTH//2, 240))
    screen.blit(count_text, count_rect)
    for i, button in enumerate(multiplayer_buttons):
        is_selected = (i == multiplayer_option and i < 2) or (i == 2 and multiplayer_option < 2)
        y_pos = 300 if i < 2 else (400 if i == 2 else 500)
        button_rect = pygame.Rect(
            button["rect"].x - 20,
            y_pos - 10,
            button["rect"].width + 40,
            button["rect"].height + 20
        )
        draw_minecraft_button(
            screen,
            button_rect,
            button["color"] if not is_selected else (min(255, button["color"][0]+30), 
                                            min(255, button["color"][1]+30), 
                                            min(255, button["color"][2]+30)),
            button["text"].get_text() if hasattr(button["text"], 'get_text') else "",
            WHITE
        )
    controls_title = game_font.render("CONTROLS:", True, GOLD)
    controls_p1 = game_font.render("Player 1: Arrow Keys (↑ ↓ ← →)", True, WHITE)
    controls_p2 = game_font.render("Player 2: WASD Keys (W,A,S,D)", True, WHITE) 
    screen.blit(controls_title, (SCREEN_WIDTH//2 - controls_title.get_width()//2, 570))
    screen.blit(controls_p1, (SCREEN_WIDTH//2 - controls_p1.get_width()//2, 600))
    screen.blit(controls_p2, (SCREEN_WIDTH//2 - controls_p2.get_width()//2, 630))
    inst_text = game_font.render("Press ESC to return to menu", True, (200, 200, 200))
    screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, 700))
def draw_difficulty_selection():
    screen.fill(DIRT_BROWN)
    title_text = title_font.render("SELECT DIFFICULTY", True, GOLD)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    for i, button in enumerate(difficulty_buttons):
        is_selected = difficulty.value == i
        button_rect = pygame.Rect(
            button["rect"].x - 20,
            button["rect"].y - 10,
            button["rect"].width + 40,
            button["rect"].height + 20
        )
        draw_minecraft_button(
            screen,
            button_rect,
            button["color"] if not is_selected else (min(255, button["color"][0]+30), 
                                            min(255, button["color"][1]+30), 
                                            min(255, button["color"][2]+30)),
            button["text"].get_text() if hasattr(button["text"], 'get_text') else "",
            WHITE
        )
    inst_text = game_font.render("Press ESC to go back", True, WHITE)
    inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
    screen.blit(inst_text, inst_rect)
def draw_area_selection():
    screen.fill(DIRT_BROWN)
    title_text = title_font.render("SELECT AREA", True, GOLD)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    for i, button in enumerate(area_buttons):
        is_selected = current_area == AREAS[i]
        button_rect = pygame.Rect(
            button["rect"].x - 20,
            button["rect"].y - 10,
            button["rect"].width + 40,
            button["rect"].height + 20
        )
        draw_minecraft_button(
            screen,
            button_rect,
            button["color"] if not is_selected else (min(255, button["color"][0]+30), 
                                            min(255, button["color"][1]+30), 
                                            min(255, button["color"][2]+30)),
            button["text"].get_text() if hasattr(button["text"], 'get_text') else "",
            WHITE
        )
    inst_text = game_font.render("Press ESC to go back", True, WHITE)
    inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
    screen.blit(inst_text, inst_rect)
def draw_game_over():
    global game_over_alpha
    if game_over_alpha < 180:
        game_over_alpha += 5
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, game_over_alpha))
    screen.blit(overlay, (0, 0))
    game_over_text = title_font.render("GAME OVER", True, RED)
    game_over_shadow = title_font.render("GAME OVER", True, (100, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2 + 3, 150 + 3))
    screen.blit(game_over_shadow, game_over_rect)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 150))
    screen.blit(game_over_text, game_over_rect)
    score_text = score_font.render(f"SCORE: {max(snake.score for snake in snakes)}", True, GOLD)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
    screen.blit(score_text, score_rect)
    high_score_text = score_font.render(f"HIGH SCORE: {high_score}", True, GOLD)
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, 300))
    screen.blit(high_score_text, high_score_rect)
    if game_mode == GameMode.MULTIPLAYER and len(snakes) > 1:
        alive_snakes = [s for s in snakes if s.alive]
        if len(alive_snakes) == 1:
            winner_color = "GREEN" if alive_snakes[0].color == GRASS_GREEN else "BLUE"
            winner_text = score_font.render(f"WINNER: PLAYER {1 if alive_snakes[0].color == GRASS_GREEN else 2}", True, alive_snakes[0].color)
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, 350))
            screen.blit(winner_text, winner_rect)
    restart_text = menu_font.render("Press SPACE to restart", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 400 if game_mode == GameMode.SINGLE else 450))
    screen.blit(restart_text, restart_rect)
    menu_text = menu_font.render("Press ESC for main menu", True, WHITE)
    menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, 480 if game_mode == GameMode.SINGLE else 530))
    screen.blit(menu_text, menu_rect)
def draw_name_input():
    screen.fill(DIRT_BROWN)
    title_text = title_font.render("ENTER YOUR NAME", True, GOLD)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
    screen.blit(title_text, title_rect)
    input_box = pygame.Rect(SCREEN_WIDTH//2 - 150, 250, 300, 50)
    draw_minecraft_button(screen, input_box, STONE_GRAY)
    text_surface = input_font.render(player_name, True, WHITE)
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
    if name_input_active and int(time.time() * 2) % 2 == 0:
        cursor_x = input_box.x + 10 + text_surface.get_width()
        pygame.draw.rect(screen, WHITE, (cursor_x, input_box.y + 10, 2, 30))
    inst_text = game_font.render("Press ENTER to confirm", True, WHITE)
    inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, 350))
    screen.blit(inst_text, inst_rect)
def draw_leaderboard():
    screen.fill(DIRT_BROWN)
    title_text = title_font.render("LEADERBOARD", True, GOLD)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
    for i, entry in enumerate(sorted_leaderboard[:10]):
        if i == 0:
            color = GOLD
            prefix = "1st"
        elif i == 1:
            color = (192, 192, 192)  # Silver
            prefix = "2nd"
        elif i == 2:
            color = (205, 127, 50)  # Bronze
            prefix = "3rd"
        else:
            color = WHITE
            prefix = f"{i+1}th"
        
        entry_text = game_font.render(
            f"{prefix}: {entry['name']} - {entry['score']} ({entry['area']}, {entry['difficulty']})", 
            True, color
        )
        screen.blit(entry_text, (SCREEN_WIDTH//2 - entry_text.get_width()//2, 150 + i*40))
    back_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
    draw_minecraft_button(screen, back_button, STONE_GRAY, "BACK", WHITE)
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    if back_button.collidepoint(mouse_pos) and mouse_clicked:
        click_sound.play()
        time.sleep(0.1)
        return True
    return False
def spawn_enemy():
    global last_enemy_spawn
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_spawn > enemy_spawn_interval:
        last_enemy_spawn = current_time
        if difficulty == Difficulty.EASY:
            if random.random() < 0.3:  
                return
            enemy_type = 0
        elif difficulty == Difficulty.MEDIUM:
            if random.random() < 0.1:  
                return
            enemy_type = random.randint(0, 1)
        else: 
            enemy_type = random.randint(0, 2)
        valid_position = False
        attempts = 0
        max_attempts = 20
        
        while not valid_position and attempts < max_attempts:
            attempts += 1
            ex = random.randrange(0, SCREEN_WIDTH - enemy_size, enemy_size)
            ey = random.randrange(0, SCREEN_HEIGHT - enemy_size, enemy_size)
            valid_position = True
            for snake in snakes:
                for block in snake.snake_list:
                    if abs(block[0] - ex) < enemy_size and abs(block[1] - ey) < enemy_size:
                        valid_position = False
                        break
                if not valid_position:
                    break
            if abs(food_x - ex) < enemy_size and abs(food_y - ey) < enemy_size:
                valid_position = False
            for wall in current_area.walls:
                wall_rect = pygame.Rect(wall)
                enemy_rect = pygame.Rect(ex, ey, enemy_size, enemy_size)
                if wall_rect.colliderect(enemy_rect):
                    valid_position = False
                    break
        if valid_position:
            dir_x, dir_y = 0, 0
            if random.random() < 0.5:
                dir_x = enemy_size if random.random() < 0.5 else -enemy_size
            else:
                dir_y = enemy_size if random.random() < 0.5 else -enemy_size
            
            enemies.append({
                'x': ex,
                'y': ey,
                'dx': dir_x,
                'dy': dir_y,
                'type': enemy_type,
                'speed': ENEMY_TYPES[enemy_type]['speed']
            })
def move_enemies():
    for enemy in enemies[:]:
        enemy['x'] += enemy['dx'] * enemy['speed']
        enemy['y'] += enemy['dy'] * enemy['speed']
        hit_wall = False
        if enemy['x'] < 0 or enemy['x'] >= SCREEN_WIDTH - enemy_size:
            enemy['dx'] *= -1
            hit_wall = True
        if enemy['y'] < 0 or enemy['y'] >= SCREEN_HEIGHT - enemy_size:
            enemy['dy'] *= -1
            hit_wall = True
        for wall in current_area.walls:
            wall_rect = pygame.Rect(wall)
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy_size, enemy_size)
            if wall_rect.colliderect(enemy_rect):
                if enemy['dx'] != 0:  
                    if (enemy_rect.right > wall_rect.left and enemy_rect.left < wall_rect.left) or \
                       (enemy_rect.left < wall_rect.right and enemy_rect.right > wall_rect.right):
                        enemy['dx'] *= -1
                else: 
                    if (enemy_rect.bottom > wall_rect.top and enemy_rect.top < wall_rect.top) or \
                       (enemy_rect.top < wall_rect.bottom and enemy_rect.bottom > wall_rect.bottom):
                        enemy['dy'] *= -1
                hit_wall = True
        if not hit_wall and random.random() < 0.02:
            if random.random() < 0.5:
                enemy['dx'] = enemy_size if random.random() < 0.5 else -enemy_size
                enemy['dy'] = 0
            else:
                enemy['dy'] = enemy_size if random.random() < 0.5 else -enemy_size
                enemy['dx'] = 0
def check_enemy_collision():
    for snake in snakes[:]:
        if not snake.alive:
            continue
        snake_head = pygame.Rect(snake.snake_list[-1][0], snake.snake_list[-1][1], snake_block, snake_block)
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy_size, enemy_size)
            if snake_head.colliderect(enemy_rect):
                snake.alive = False
                break
def check_wall_collision():
    for snake in snakes[:]:
        if not snake.alive:
            continue
        snake_head = pygame.Rect(snake.snake_list[-1][0], snake.snake_list[-1][1], snake_block, snake_block)
        for wall in current_area.walls:
            wall_rect = pygame.Rect(wall)
            if snake_head.colliderect(wall_rect):
                snake.alive = False
                break
def check_snake_collisions():
    if len(snakes) < 2:
        return   
    for i, snake1 in enumerate(snakes):
        if not snake1.alive:
            continue    
        snake1_head = pygame.Rect(snake1.snake_list[-1][0], snake1.snake_list[-1][1], snake_block, snake_block)
        for snake2 in snakes:
            for block in snake2.snake_list[:-1]:
                if snake1_head.colliderect(pygame.Rect(block[0], block[1], snake_block, snake_block)):
                    snake1.alive = False
                    break
            if not snake1.alive:
                break
def check_food_collision():
    global food_x, food_y, food_type
    for snake in snakes:
        if not snake.alive:
            continue    
        if abs(snake.x - food_x) < snake_block and abs(snake.y - food_y) < snake_block:
            snake.score += 1
            snake.snake_length += 1
            food_x = random.randrange(0, SCREEN_WIDTH - food_block, food_block)
            food_y = random.randrange(0, SCREEN_HEIGHT - food_block, food_block)
            food_type = random.choice(["apple", "berry", "steak"])
            makan_sound.play()
def reset_game():
    global food_x, food_y, food_type, enemies
    for i, snake in enumerate(snakes):
        snake.snake_list = []
        snake.snake_length = 1
        snake.x = SCREEN_WIDTH // 2 + (-100 if i == 0 else 100)
        snake.y = SCREEN_HEIGHT // 2
        snake.dx = 0
        snake.dy = 0
        snake.alive = True
        snake.score = 0
    food_x = random.randrange(0, SCREEN_WIDTH - food_block, food_block)
    food_y = random.randrange(0, SCREEN_HEIGHT - food_block, food_block)
    food_type = random.choice(["apple", "berry", "steak"])
    enemies = []
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == GameState.MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    menu_option = (menu_option + 1) % len(buttons)
                    gerakan_sound.play()
                elif event.key == pygame.K_UP:
                    menu_option = (menu_option - 1) % len(buttons)
                    gerakan_sound.play()
                elif event.key == pygame.K_RETURN:
                    click_sound.play()
                    if menu_option == 0:  
                        game_state = GameState.NAME_INPUT
                        player_name = ""
                        name_input_active = True
                    elif menu_option == 1: 
                        game_state = GameState.LEVEL_SELECT
                    elif menu_option == 2: 
                        game_state = GameState.AREA_SELECT
                    elif menu_option == 3: 
                        game_state = GameState.LEADERBOARD
                    elif menu_option == 4: 
                        game_state = GameState.MULTIPLAYER_SETUP
                        multiplayer_option = 0
                    elif menu_option == 5: 
                        running = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        elif game_state == GameState.MULTIPLAYER_SETUP:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    multiplayer_option = (multiplayer_option + 1) % 4
                    if multiplayer_option == 3: 
                        multiplayer_option = 3
                    gerakan_sound.play()
                elif event.key == pygame.K_UP:
                    multiplayer_option = (multiplayer_option - 1) % 4
                    if multiplayer_option == 3:  
                        multiplayer_option = 2
                    gerakan_sound.play()
                elif event.key == pygame.K_RETURN:
                    click_sound.play()
                    if multiplayer_option == 0:  
                        snakes = [player1]
                        game_mode = GameMode.SINGLE
                        game_state = GameState.NAME_INPUT
                        player_name = ""
                        name_input_active = True
                    elif multiplayer_option == 1:  
                        snakes = [player1, player2]
                        game_mode = GameMode.MULTIPLAYER
                        player_name = "Multiplayer"
                        game_state = GameState.PLAYING
                        reset_game()
                    elif multiplayer_option == 2:  
                        if multiplayer_option < 2:
                            game_state = GameState.PLAYING
                            reset_game()
                    elif multiplayer_option == 3: 
                        game_state = GameState.MENU
                elif event.key == pygame.K_ESCAPE:
                    game_state = GameState.MENU
        elif game_state == GameState.LEVEL_SELECT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    difficulty = Difficulty((difficulty.value + 1) % 3)
                    click_sound.play()
                elif event.key == pygame.K_UP:
                    difficulty = Difficulty((difficulty.value - 1) % 3)
                    click_sound.play()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    game_state = GameState.MENU
        elif game_state == GameState.AREA_SELECT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    current_area = AREAS[(AREAS.index(current_area) + 1) % len(AREAS)]
                    click_sound.play()
                elif event.key == pygame.K_UP:
                    current_area = AREAS[(AREAS.index(current_area) - 1) % len(AREAS)]
                    click_sound.play()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    game_state = GameState.MENU
        elif game_state == GameState.PLAYING:
            if event.type == pygame.KEYDOWN:
                for snake in snakes:
                    if not snake.alive:
                        continue
                    if event.key == snake.controls["left"] and snake.dx != snake_block:
                        snake.dx = -snake_block
                        snake.dy = 0
                        gerakan_sound.play()
                    elif event.key == snake.controls["right"] and snake.dx != -snake_block:
                        snake.dx = snake_block
                        snake.dy = 0
                        gerakan_sound.play()
                    elif event.key == snake.controls["up"] and snake.dy != snake_block:
                        snake.dx = 0
                        snake.dy = -snake_block
                        gerakan_sound.play()
                    elif event.key == snake.controls["down"] and snake.dy != -snake_block:
                        snake.dx = 0
                        snake.dy = snake_block
                        gerakan_sound.play()
                if event.key == pygame.K_ESCAPE:
                    game_state = GameState.MENU
        elif game_state == GameState.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    click_sound.play()
                    reset_game()
                    game_state = GameState.PLAYING
                    game_over_alpha = 0
                elif event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    game_state = GameState.MENU
                    game_over_alpha = 0
        elif game_state == GameState.NAME_INPUT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_name.strip():
                        click_sound.play()
                        reset_game()
                        game_state = GameState.PLAYING
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    game_state = GameState.MENU
                else:
                    if len(player_name) < 12 and event.unicode.isalnum():
                        player_name += event.unicode
        
        elif game_state == GameState.LEADERBOARD:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                click_sound.play()
                game_state = GameState.MENU
    if game_state == GameState.PLAYING:
        for snake in snakes:
            if not snake.alive:
                continue    
            snake.x += snake.dx
            snake.y += snake.dy
            if snake.x < 0 or snake.x >= SCREEN_WIDTH or snake.y < 0 or snake.y >= SCREEN_HEIGHT:
                snake.alive = False
                game_over_sound.play()
            snake_head = [snake.x, snake.y]
            snake.snake_list.append(snake_head)
            if len(snake.snake_list) > snake.snake_length:
                del snake.snake_list[0]
            for block in snake.snake_list[:-1]:
                if block == snake_head:
                    snake.alive = False
                    game_over_sound.play()
        check_wall_collision()
        check_enemy_collision()
        if game_mode == GameMode.MULTIPLAYER:
            check_snake_collisions()
        check_food_collision()
        alive_snakes = [s for s in snakes if s.alive]
        if not alive_snakes:
            game_state = GameState.GAME_OVER
            current_score = max(snake.score for snake in snakes)
            if current_score > high_score:
                high_score = current_score
            if game_mode == GameMode.SINGLE:
                leaderboard.append({
                    "name": player_name,
                    "score": current_score,
                    "difficulty": difficulty.name,
                    "area": current_area.name,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                save_leaderboard()
        spawn_enemy()
        move_enemies()
    if game_state == GameState.MENU:
        draw_menu()
    elif game_state == GameState.MULTIPLAYER_SETUP:
        draw_multiplayer_setup()
    elif game_state == GameState.LEVEL_SELECT:
        draw_difficulty_selection()
    elif game_state == GameState.AREA_SELECT:
        draw_area_selection()
    elif game_state == GameState.PLAYING:
        draw_background()
        draw_walls()
        pulse_anim = (pulse_anim + 0.1) % (2 * math.pi)
        pulse = 0.5 * math.sin(pulse_anim)
        draw_food(food_x, food_y, pulse, food_type)
        draw_enemies()
        for snake in snakes:
            draw_snake(snake.snake_list, snake.color, snake.alive)
        if game_mode == GameMode.SINGLE:
            score_text = score_font.render(f"Score: {snakes[0].score}", True, WHITE)
            score_shadow = score_font.render(f"Score: {snakes[0].score}", True, BLACK)
            screen.blit(score_shadow, (21, 21))
            screen.blit(score_text, (20, 20))
        else:
            p1_score = score_font.render(f"P1: {snakes[0].score}", True, snakes[0].color)
            p1_shadow = score_font.render(f"P1: {snakes[0].score}", True, BLACK)
            p2_score = score_font.render(f"P2: {snakes[1].score}", True, snakes[1].color)
            p2_shadow = score_font.render(f"P2: {snakes[1].score}", True, BLACK)
            screen.blit(p1_shadow, (21, 21))
            screen.blit(p2_shadow, (SCREEN_WIDTH - p2_shadow.get_width() - 19, 21))
            screen.blit(p1_score, (20, 20))
            screen.blit(p2_score, (SCREEN_WIDTH - p2_score.get_width() - 20, 20))
        if game_mode == GameMode.SINGLE:
            name_text = game_font.render(f"Player: {player_name}", True, WHITE)
            name_shadow = game_font.render(f"Player: {player_name}", True, BLACK)
            screen.blit(name_shadow, (21, 61))
            screen.blit(name_text, (20, 60))
        diff_text = game_font.render(f"Difficulty: {difficulty.name}", True, WHITE)
        diff_shadow = game_font.render(f"Difficulty: {difficulty.name}", True, BLACK)
        screen.blit(diff_shadow, (21, 91))
        screen.blit(diff_text, (20, 90))
        area_text = game_font.render(f"Area: {current_area.name}", True, WHITE)
        area_shadow = game_font.render(f"Area: {current_area.name}", True, BLACK)
        screen.blit(area_shadow, (21, 121))
        screen.blit(area_text, (20, 120))
    elif game_state == GameState.GAME_OVER:
        draw_background()
        draw_walls()
        draw_food(food_x, food_y, 0, food_type)
        draw_enemies()
        for snake in snakes:
            draw_snake(snake.snake_list, snake.color, snake.alive)
        draw_game_over()
    elif game_state == GameState.NAME_INPUT:
        draw_name_input()
    elif game_state == GameState.LEADERBOARD:
        if draw_leaderboard():
            game_state = GameState.MENU
    
    pygame.display.flip()

    if difficulty == Difficulty.EASY:
        clock.tick(snake_speed)
    elif difficulty == Difficulty.MEDIUM:
        clock.tick(snake_speed + 5)
    else: 
        clock.tick(snake_speed + 10)

pygame.quit()
sys.exit()