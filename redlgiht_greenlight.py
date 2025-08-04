import pygame
import sys
import random

# --- Constants ---
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 50  
PLAYER_SPEED = 0.7
AI_SPEED = 0.8
GOAL_LINE = 10
NUM_AI = 8

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red Light Green Light - Road Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# --- Asset Loading ---
def load_image(filename, size=None):
    try:
        img = pygame.image.load(filename).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        print(f"[!] Failed to load: {filename}")
        return None

# Load images
doll_img = load_image("doll.png", (120, 180)) 
player_img = load_image("bluecar.png", (PLAYER_SIZE, PLAYER_SIZE))
ai_img = load_image("redcar.png", (PLAYER_SIZE, PLAYER_SIZE))

# --- Procedural Road Background ---
def create_road_bg():
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((30, 30, 30))  # Dark gray background
    
    # Draw road markings (full width)
    pygame.draw.rect(bg, (50, 50, 50), (0, HEIGHT//3, WIDTH, HEIGHT//3))
    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(bg, (200, 200, 0), (WIDTH//2 - 5, y, 10, 20))
    return bg

road_bg = create_road_bg()

# --- Player Class ---
class Player:
    def __init__(self, x, y, image, is_human=False):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.image = image
        self.is_human = is_human
        self.alive = True
        self.won = False
        self.speed = PLAYER_SPEED if is_human else AI_SPEED

    def move(self, dx, dy):
        if not self.alive or self.won:
            return
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(WIDTH - PLAYER_SIZE, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - PLAYER_SIZE, self.rect.y))

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            color = (0, 100, 255) if self.is_human else (255, 50, 50)
            pygame.draw.rect(surface, color, self.rect)

# --- Game Functions ---
def draw_light(state):
    screen.blit(road_bg, (0, 0))
    
    # Draw doll
    if doll_img:
        screen.blit(doll_img, (120, 20))
    
    # Traffic light with text
    color = (0, 255, 0) if state == "green" else (255, 0, 0)
    text_color = (200, 255, 200) if state == "green" else (255, 200, 200)
    status_text = "GO!" if state == "green" else "STOP!"
    
    pygame.draw.circle(screen, color, (50, 40), 20)
    pygame.draw.circle(screen, (min(255, color[0]+100), min(255, color[1]+100), min(255, color[2]+100)), 
                      (50, 40), 10)
    
    text_surface = small_font.render(status_text, True, text_color)
    screen.blit(text_surface, (30, 65))
    
    # Finish line
    for x in range(0, WIDTH, 20):
        line_color = (255, 255, 0) if (x//20) % 2 == 0 else (0, 0, 0)
        pygame.draw.rect(screen, line_color, (x, GOAL_LINE, 20, 5))

def reset():
    players = []
    start_y = HEIGHT - 100  # Same baseline for all
    
    # Human player (center)
    players.append(Player(WIDTH//2 - PLAYER_SIZE//2, start_y, player_img, True))
    
    # AI players - evenly spaced across full width
    spacing = WIDTH // (NUM_AI + 1)
    for i in range(NUM_AI):
        x = spacing * (i + 1) - PLAYER_SIZE//2
        # Ensure cars stay within bounds
        x = max(PLAYER_SIZE//2, min(WIDTH - PLAYER_SIZE//2, x))
        players.append(Player(x, start_y, ai_img))
    
    return players, "green", 0, random.uniform(2.0, 4.0), False, False

# --- Main Game Loop ---
def main():
    players, game_state, timer, light_duration, lost, won = reset()
    
    while True:
        draw_light(game_state)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (lost or won) and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                players, game_state, timer, light_duration, lost, won = reset()

        # Player movement
        keys = pygame.key.get_pressed()
        human = players[0]
        if not lost and not won and human.alive:
            dx, dy = 0, 0
            if keys[pygame.K_UP]: dy -= human.speed
            if keys[pygame.K_DOWN]: dy += human.speed
            if keys[pygame.K_LEFT]: dx -= human.speed
            if keys[pygame.K_RIGHT]: dx += human.speed
            
            if (dx != 0 or dy != 0) and game_state == "red":
                lost = True
            human.move(dx, dy)

        # AI movement
        if game_state == "green":
            for ai in players[1:]:
                if ai.alive and random.random() < 0.03:
                    ai.move(0, -ai.speed)

        # Win/lose checks
        for p in players:
            if p.rect.y <= GOAL_LINE and not p.won:
                p.won = True
                if p.is_human:
                    won = True

        # Light switching
        timer += 1/60
        if timer >= light_duration:
            game_state = "red" if game_state == "green" else "green"
            timer = 0
            light_duration = random.uniform(1.5, 3.5)

        # Draw all players
        for p in players:
            if p.alive or p.won:
                p.draw(screen)

        # UI Messages
        if lost:
            msg = font.render("CRASHED! (Press R)", True, (255, 50, 50))
            screen.blit(msg, (WIDTH//2 - 120, HEIGHT//2))
        elif won:
            msg = font.render("FINISH LINE! (Press R)", True, (50, 255, 50))
            screen.blit(msg, (WIDTH//2 - 140, HEIGHT//2))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()