import pygame
import random
import sys
import math

pygame.init()

# Window setup
W, H = 450, 800
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Highway Racer")
clock = pygame.time.Clock()

# Fonts
FONT_LABEL = pygame.font.SysFont("arial", 12, bold=True)
FONT_VALUE = pygame.font.SysFont("arial", 22, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 32, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 38, bold=True)

# Color Palette
BG_OUTER = (0, 100, 210)
HUD_BG = (10, 30, 80)
HUD_BORDER = (0, 180, 255)
ROAD_COLOR = (45, 52, 64)
YELLOW_LINE = (255, 200, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
GOLD_DARK = (218, 165, 32)
SAND = (238, 214, 136)
WATER = (0, 160, 240)
GRASS = (46, 175, 40)
GRASS_DARK = (30, 130, 25)

# Game Dimensions
ROAD_LEFT, ROAD_RIGHT = 80, 370
LANES = [120, 185, 250, 315]

# Drawing Helper Functions
def draw_rounded_rect(surface, color, rect, radius=10, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)

def draw_car(x, y, body_color, stripe=False):
    x, y = int(x), int(y)
    # Shadow
    pygame.draw.rect(screen, (15, 20, 25), (x-18, y-33, 36, 70), border_radius=10)
    # Body
    pygame.draw.rect(screen, body_color, (x-18, y-35, 36, 68), border_radius=10)
    
    # Racing Stripe for Player
    if stripe:
        pygame.draw.rect(screen, WHITE, (x-4, y-35, 8, 68))
        
    # Roof & Windshields
    pygame.draw.rect(screen, (30, 35, 45), (x-13, y-20, 26, 38), border_radius=6)
    pygame.draw.rect(screen, body_color, (x-11, y-10, 22, 20))
    
    # Lights
    pygame.draw.rect(screen, (255, 240, 150), (x-15, y-34, 6, 4), border_radius=2)
    pygame.draw.rect(screen, (255, 240, 150), (x+9, y-34, 6, 4), border_radius=2)
    pygame.draw.rect(screen, (240, 40, 40), (x-15, y+29, 6, 4), border_radius=2)
    pygame.draw.rect(screen, (240, 40, 40), (x+9, y+29, 6, 4), border_radius=2)

def draw_cone(x, y):
    x, y = int(x), int(y)
    # Base
    pygame.draw.ellipse(screen, (100, 40, 0), (x-12, y+6, 24, 8))
    pygame.draw.rect(screen, (220, 70, 10), (x-10, y+4, 20, 5), border_radius=2)
    # Cone body
    pygame.draw.polygon(screen, (240, 80, 20), [(x, y-16), (x-9, y+4), (x+9, y+4)])
    # White stripes
    pygame.draw.polygon(screen, WHITE, [(x, y-10), (x-5, y-1), (x+5, y-1)])

def draw_coin(x, y):
    x, y = int(x), int(y)
    pygame.draw.circle(screen, GOLD_DARK, (x, y), 11)
    pygame.draw.circle(screen, GOLD, (x, y), 9)
    # Dollar symbol
    font_coin = pygame.font.SysFont("arial", 12, bold=True)
    txt = font_coin.render("$", True, (150, 100, 0))
    screen.blit(txt, txt.get_rect(center=(x, y)))

def draw_hud(score, speed, paused):
    # Main outer border
    draw_rounded_rect(screen, HUD_BORDER, (10, 10, W-20, 80), radius=12, width=3)
    
    # Card 1: Score
    draw_rounded_rect(screen, HUD_BG, (16, 16, 140, 68), radius=10)
    draw_rounded_rect(screen, HUD_BORDER, (16, 16, 140, 68), radius=10, width=2)
    # Trophy Icon
    pygame.draw.polygon(screen, GOLD, [(32, 32), (48, 32), (44, 46), (36, 46)])
    pygame.draw.rect(screen, GOLD, (38, 46, 4, 8))
    pygame.draw.rect(screen, GOLD, (34, 52, 12, 3))
    # Score Text
    lbl = FONT_LABEL.render("SCORE", True, WHITE)
    screen.blit(lbl, (60, 24))
    val = FONT_VALUE.render(str(score), True, GOLD)
    screen.blit(val, (60, 40))

    # Card 2: Speed
    draw_rounded_rect(screen, HUD_BG, (164, 16, 140, 68), radius=10)
    draw_rounded_rect(screen, HUD_BORDER, (164, 16, 140, 68), radius=10, width=2)
    # Speedometer Icon
    pygame.draw.circle(screen, HUD_BORDER, (190, 48), 12, width=2)
    pygame.draw.line(screen, WHITE, (190, 48), (198, 42), 2)
    # Speed Text
    lbl2 = FONT_LABEL.render("SPEED", True, WHITE)
    screen.blit(lbl2, (210, 22))
    val2 = FONT_VALUE.render(f"{int(speed*20)}", True, GOLD)
    screen.blit(val2, (210, 38))
    unit = FONT_LABEL.render("KM/H", True, WHITE)
    screen.blit(unit, (210, 60))

    # Card 3: Pause Button
    draw_rounded_rect(screen, HUD_BG, (312, 16, 122, 68), radius=10)
    draw_rounded_rect(screen, HUD_BORDER, (312, 16, 122, 68), radius=10, width=2)
    
    pause_rect = pygame.Rect(312, 16, 122, 68)
    if paused:
        # Play Triangle
        pygame.draw.polygon(screen, WHITE, [(365, 36), (365, 60), (385, 48)])
    else:
        # Pause Bars
        pygame.draw.rect(screen, WHITE, (360, 36, 8, 24), border_radius=2)
        pygame.draw.rect(screen, WHITE, (376, 36, 8, 24), border_radius=2)

    return pause_rect

def reset_game():
    return {
        "x": LANES[1],
        "y": H - 120,
        "traffic": [],
        "coins": [],
        "cones": [],
        "line_offset": 0,
        "speed": 6.0,
        "score": 0,
        "spawn_timer": 0,
        "over": False,
        "paused": False
    }

# Main Game Loop
game = reset_game()
running = True

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_p:
                game["paused"] = not game["paused"]
            if event.key == pygame.K_r and game["over"]:
                game = reset_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Check pause button click
            if 312 <= mx <= 434 and 16 <= my <= 84:
                game["paused"] = not game["paused"]

    keys = pygame.key.get_pressed()

    if not game["over"] and not game["paused"]:
        # Controls
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            game["x"] -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            game["x"] += 5
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            game["speed"] = min(11.0, game["speed"] + 0.05)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            game["speed"] = max(3.0, game["speed"] - 0.08)

        # Keep inside road borders
        game["x"] = max(ROAD_LEFT + 22, min(ROAD_RIGHT - 22, game["x"]))

        # Move road graphics
        game["line_offset"] = (game["line_offset"] + game["speed"]) % 60

        # Spawning entities
        game["spawn_timer"] += 1
        if game["spawn_timer"] > 40:
            game["spawn_timer"] = 0
            lane = random.choice(LANES)
            spawn_type = random.choice(["car", "car", "coin", "cone"])

            if spawn_type == "car":
                game["traffic"].append({
                    "x": lane, "y": -80,
                    "color": random.choice([(140, 30, 210), (0, 180, 240), (240, 200, 0), (40, 200, 80)]),
                    "speed": random.uniform(2.0, 3.5)
                })
            elif spawn_type == "coin":
                # Spawn vertical chain of coins
                for c in range(3):
                    game["coins"].append({"x": lane, "y": -60 - (c * 35)})
            elif spawn_type == "cone":
                game["cones"].append({"x": lane + random.randint(-10, 10), "y": -60})

        player_rect = pygame.Rect(game["x"] - 15, game["y"] - 30, 30, 60)

        # Update Traffic Cars
        for enemy in game["traffic"][:]:
            enemy["y"] += enemy["speed"] + game["speed"] * 0.5
            enemy_rect = pygame.Rect(enemy["x"] - 15, enemy["y"] - 30, 30, 60)
            if player_rect.colliderect(enemy_rect):
                game["over"] = True
            if enemy["y"] > H + 80:
                game["traffic"].remove(enemy)

        # Update Cones
        for cone in game["cones"][:]:
            cone["y"] += game["speed"]
            cone_rect = pygame.Rect(cone["x"] - 10, cone["y"] - 10, 20, 20)
            if player_rect.colliderect(cone_rect):
                game["over"] = True
            if cone["y"] > H + 50:
                game["cones"].remove(cone)

        # Update Coins
        for coin in game["coins"][:]:
            coin["y"] += game["speed"]
            coin_rect = pygame.Rect(coin["x"] - 10, coin["y"] - 10, 20, 20)
            if player_rect.colliderect(coin_rect):
                game["score"] += 50
                game["coins"].remove(coin)
            elif coin["y"] > H + 50:
                game["coins"].remove(coin)

    # DRAWING SCENE
    screen.fill(BG_OUTER)

    # Left Side: Water & Beach
    pygame.draw.rect(screen, WATER, (0, 0, 50, H))
    pygame.draw.rect(screen, SAND, (50, 0, 30, H))
    # Simple shoreline detail
    for y_pos in range(0, H, 40):
        wy = (y_pos + int(game["line_offset"])) % H
        pygame.draw.circle(screen, WHITE, (50, wy), 4)

    # Right Side: Grass & Trees
    pygame.draw.rect(screen, GRASS, (ROAD_RIGHT, 0, W - ROAD_RIGHT, H))
    for y_pos in range(-40, H, 70):
        ty = (y_pos + int(game["line_offset"])) % (H + 80) - 40
        pygame.draw.circle(screen, GRASS_DARK, (ROAD_RIGHT + 35, ty), 16)
        pygame.draw.circle(screen, GRASS, (ROAD_RIGHT + 33, ty - 2), 14)

    # Road Surface
    pygame.draw.rect(screen, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, H))
    
    # Double Yellow Edges
    pygame.draw.rect(screen, YELLOW_LINE, (ROAD_LEFT + 4, 0, 3, H))
    pygame.draw.rect(screen, YELLOW_LINE, (ROAD_LEFT + 10, 0, 3, H))
    pygame.draw.rect(screen, YELLOW_LINE, (ROAD_RIGHT - 13, 0, 3, H))
    pygame.draw.rect(screen, YELLOW_LINE, (ROAD_RIGHT - 7, 0, 3, H))

    # White Lane Markings
    for lane_x in [152, 225, 297]:
        for y_pos in range(-60, H, 60):
            yy = y_pos + game["line_offset"]
            pygame.draw.rect(screen, WHITE, (lane_x - 2, yy, 4, 28))

    # Draw Game Objects
    for coin in game["coins"]:
        draw_coin(coin["x"], coin["y"])

    for cone in game["cones"]:
        draw_cone(cone["x"], cone["y"])

    for enemy in game["traffic"]:
        draw_car(enemy["x"], enemy["y"], enemy["color"])

    # Draw Player Car (Red with white stripe)
    draw_car(game["x"], game["y"], (230, 35, 45), stripe=True)

    # Blue Window Border Outline
    draw_rounded_rect(screen, HUD_BORDER, (5, 5, W-10, H-10), radius=16, width=4)

    # HUD Overlays
    draw_hud(game["score"], game["speed"], game["paused"])

    # Pause / Game Over Overlays
    if game["over"]:
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((10, 15, 30, 210))
        screen.blit(shade, (0, 0))
        
        lbl_over = FONT_TITLE.render("CRASHED!", True, (255, 60, 60))
        screen.blit(lbl_over, lbl_over.get_rect(center=(W//2, 320)))
        
        lbl_score = FONT_VALUE.render(f"FINAL SCORE: {game['score']}", True, WHITE)
        screen.blit(lbl_score, lbl_score.get_rect(center=(W//2, 380)))
        
        lbl_restart = FONT_LABEL.render("Press 'R' to Restart", True, HUD_BORDER)
        screen.blit(lbl_restart, lbl_restart.get_rect(center=(W//2, 430)))

    elif game["paused"]:
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 140))
        screen.blit(shade, (0, 0))
        
        lbl_pause = FONT_BIG.render("PAUSED", True, WHITE)
        screen.blit(lbl_pause, lbl_pause.get_rect(center=(W//2, H//2)))

    pygame.display.flip()

pygame.quit()
sys.exit()