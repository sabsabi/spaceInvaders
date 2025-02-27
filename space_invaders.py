import pygame
import sys
import random
import json
from screens import show_start_screen

# Initialize pygame and sound
pygame.init()
pygame.mixer.init()

# Load sound effects
shoot_sound = pygame.mixer.Sound('sounds/shoot.wav')
explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')
ufo_sound = pygame.mixer.Sound('sounds/ufo.wav')
game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')

# Adjust sound volumes
shoot_sound.set_volume(0.3)
explosion_sound.set_volume(0.4)
ufo_sound.set_volume(0.2)
game_over_sound.set_volume(0.5)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

from colors import Colors

# Use color constants from the Colors class
WHITE = Colors.WHITE
BLACK = Colors.BLACK
GREEN = Colors.GREEN
RED = Colors.RED

# Game settings
FPS = 60

# Spaceship settings
SHIP_WIDTH = 50
SHIP_HEIGHT = 30
SHIP_COLOR = GREEN
SHIP_SPEED = 5

# Bullet settings
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_COLOR = RED
BULLET_SPEED = 7

# Enemy Bullet settings
ENEMY_BULLET_WIDTH = 5
ENEMY_BULLET_HEIGHT = 10
ENEMY_BULLET_COLOR = (255, 255, 0)
ENEMY_BULLET_SPEED = 5

# Shooting probability for enemies
ENEMY_SHOOT_PROB = 0.005

# UFO settings
UFO_SPEED = 3
UFO_SPAWN_PROB = 0.004
UFO_BONUS_POINTS = 150
UFO_SHOOT_PROB = 0.005

# Power-up settings
POWERUP_SPEED = 2
POWERUP_DURATION = 300  # frames
POWERUP_DROP_CHANCE = 0.1  # 10% chance to drop from destroyed enemies

# Enemy settings
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_COLOR = (0, 0, 255)
ENEMY_SPEED = 1
ENEMY_DROP = 20

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Space Invaders')

clock = pygame.time.Clock()

# Define the spaceship class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.speed = POWERUP_SPEED
        self.active = True
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Load the power-up sprite
        try:
            self.image = pygame.transform.scale(pygame.image.load('sprites/powerUp.png'), (self.width, self.height))
        except:
            # Fallback to a colored rectangle if image not found
            self.image = None
            
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False
        self.rect.y = self.y
        
    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            # Use different colors for different power-up types
            color = (255, 255, 0) if self.type == 'double_shot' else (0, 255, 255)  # Yellow for double shot, cyan for shield
            pygame.draw.rect(surface, color, self.rect)

class Spaceship:
    def __init__(self):
        self.width = SHIP_WIDTH
        self.height = SHIP_HEIGHT
        self.lives = 1  # Default is 3 lives
        self.respawn_timer = 0
        self.respawn_delay = 60  # 1 second at 60 FPS
        self.flash_interval = 10  # Flash every 10 frames
        self.invulnerable = False
        self.reset_position()
        # Load and resize spaceship image
        self.image = pygame.transform.scale(pygame.image.load('sprites/ship.png'), (SHIP_WIDTH, SHIP_HEIGHT))
        # Create a smaller version for lives display
        self.life_image = pygame.transform.scale(pygame.image.load('sprites/ship.png'), (25, 15))
        self.destroyed = False
        # Power-up states
        self.double_shot = False
        self.shield = False
        self.power_up_timer = 0
        
    def reset_position(self):
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = SHIP_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def respawn(self):
        if self.lives > 0:
            self.reset_position()
            self.destroyed = False
            self.respawn_timer = self.respawn_delay
            self.invulnerable = True
            
    def update(self):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.invulnerable = False

    def move(self, dx):
        self.x += dx * self.speed
        # Keep the spaceship within the screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        self.rect.x = self.x

    def draw(self, surface):
        # Flash during invulnerability by only drawing every other interval
        if not self.invulnerable or (self.respawn_timer // self.flash_interval) % 2 == 0:
            surface.blit(self.image, (self.x, self.y))

# Define the bullet class
class Bullet:
    def __init__(self, x, y):
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True
        
    def update(self):
        self.y -= self.speed
        if self.y < 0:
            self.active = False
        self.rect.y = self.y
        
    def draw(self, surface):
        pygame.draw.rect(surface, BULLET_COLOR, self.rect)

# Define the enemy bullet class
class EnemyBullet:
    def __init__(self, x, y):
        self.width = ENEMY_BULLET_WIDTH
        self.height = ENEMY_BULLET_HEIGHT
        self.x = x
        self.y = y
        self.speed = ENEMY_BULLET_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, ENEMY_BULLET_COLOR, self.rect)

# Define the explosion class
class Explosion:
    def __init__(self, x, y, permanent=False):
        self.image = pygame.transform.scale(pygame.image.load('sprites/explosion.png'), (50, 50))
        self.x = x
        self.y = y
        self.duration = 20
        self.frame = 0
        self.active = True
        self.permanent = permanent

    def update(self):
        if not self.permanent:
            self.frame += 1
            if self.frame >= self.duration:
                self.active = False

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# Define the UFO class
class UFO:
    def __init__(self, x, direction=1):
        self.image = pygame.transform.scale(pygame.image.load('sprites/ufo.png'), (60, 30))
        self.x = x
        self.y = 20  # fixed y-position near the top
        self.direction = direction  # 1 for right, -1 for left
        self.speed = UFO_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.active = True

    def update(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x
        if self.direction == 1 and self.x > SCREEN_WIDTH:
            self.active = False
        elif self.direction == -1 and self.x + self.rect.width < 0:
            self.active = False

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# Define the enemy class
class Enemy:
    def __init__(self, x, y):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Load and resize enemy images for animation
        self.image_up = pygame.transform.scale(pygame.image.load('sprites/enemyUP.png'), (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image_down = pygame.transform.scale(pygame.image.load('sprites/enemyDown.png'), (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.alive = True
        self.animation_timer = 0
        self.animation_interval = 20  # Adjust this value to control animation speed
        self.use_up_image = True

    def update(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.use_up_image = not self.use_up_image

    def draw(self, surface):
        if self.alive:
            current_image = self.image_up if self.use_up_image else self.image_down
            surface.blit(current_image, (self.x, self.y))

# Create enemy formation
def create_enemies(rows, cols, x_offset=50, y_offset=50, padding=10):
    enemies = []
    for row in range(rows):
        for col in range(cols):
            x = x_offset + col * (ENEMY_WIDTH + padding)
            y = y_offset + row * (ENEMY_HEIGHT + padding)
            enemy = Enemy(x, y)
            enemies.append(enemy)
    return enemies

# Main game loop
def load_high_scores():
    default_scores = [
        {'name': 'CPU', 'score': 2000},
        {'name': 'CPU', 'score': 1500},
        {'name': 'CPU', 'score': 1000},
        {'name': 'CPU', 'score': 500},
        {'name': 'CPU', 'score': 250}
    ]
    
    try:
        with open('high_scores.json', 'r') as f:
            return json.load(f)
    except:
        with open('high_scores.json', 'w') as f:
            json.dump(default_scores, f)
        return default_scores

def is_high_score(score):
    scores = load_high_scores()
    if len(scores) < 5:
        return True
    lowest_score = min(s['score'] for s in scores)
    return score > lowest_score

def save_high_score(score, name):
    scores = load_high_scores()
    scores.append({'name': name, 'score': score})
    # Sort by score (descending) and then by name
    scores.sort(key=lambda x: (-x['score'], x['name']))
    scores = scores[:5]  # Keep only top 5 scores
    try:
        with open('high_scores.json', 'w') as f:
            json.dump(scores, f)
    except Exception as e:
        print(f'Error saving high score: {e}')

def get_player_name(screen, font):
    name = ''
    input_active = True
    input_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 32)
    clock = pygame.time.Clock()
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10:  # Limit name length
                        if event.unicode.isalnum():  # Only allow letters and numbers
                            name += event.unicode
        
        screen.fill(BLACK)
        
        # Draw prompt
        prompt_text = font.render('New High Score! Enter Your Name:', True, WHITE)
        screen.blit(prompt_text, (SCREEN_WIDTH//2 - prompt_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # Draw input box
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        
        # Draw input text
        text_surface = font.render(name, True, WHITE)
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return name if name else 'Unknown'

def main():
    # Show the start screen
    show_start_screen(screen)
    running = True

    spaceship = Spaceship()
    player_bullets = []  # List to store player bullets
    enemies = create_enemies(5, 10)
    enemy_bullets = []
    explosions = []
    ufo = None
    enemy_dx = ENEMY_SPEED
    enemy_move_down = False

    score = 0
    font = pygame.font.SysFont(None, 36)
    game_over = False
    power_ups = []
    high_scores = load_high_scores()
    
    def draw_lives(surface, ship):
        # Draw lives in top-left corner
        for i in range(ship.lives):
            surface.blit(ship.life_image, (10 + i * 30, 40))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to quit the game
            # Fire bullet when space is pressed and there's no active bullet
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE:
                    active_bullets = len([b for b in player_bullets if b.active])
                    max_bullets = 2 if spaceship.double_shot else 1
                    
                    if active_bullets < max_bullets:
                        if spaceship.double_shot and active_bullets == 0:
                            # Create two bullets side by side
                            player_bullets.append(Bullet(spaceship.x + 10, spaceship.y))
                            player_bullets.append(Bullet(spaceship.x + spaceship.width - 10, spaceship.y))
                            shoot_sound.play()
                        elif not spaceship.double_shot and active_bullets == 0:
                            # Single bullet from the middle
                            player_bullets.append(Bullet(spaceship.x + spaceship.width // 2 - BULLET_WIDTH // 2, spaceship.y))
                            shoot_sound.play()
            
        keys = pygame.key.get_pressed()
        if not game_over:
            spaceship.update()
            if not spaceship.destroyed:
                if keys[pygame.K_LEFT]:
                    spaceship.move(-1)
                if keys[pygame.K_RIGHT]:
                    spaceship.move(1)

        # Enemy movement: check if any enemy will cross screen boundary in the next move
        drop = False
        for enemy in enemies:
            if enemy.alive:
                if (enemy.x + enemy_dx < 0) or (enemy.x + enemy.width + enemy_dx > SCREEN_WIDTH):
                    drop = True
                    break

        if drop:
            enemy_dx = -enemy_dx
            for enemy in enemies:
                if enemy.alive:
                    enemy.update(0, ENEMY_DROP)
        else:
            for enemy in enemies:
                if enemy.alive:
                    enemy.update(enemy_dx, 0)

        # Update player bullets and check for collisions
        for bullet in player_bullets:
            if bullet.active:
                bullet.update()
                # Check collision with enemies
                for enemy in enemies:
                    if enemy.alive and bullet.rect.colliderect(enemy.rect):
                        enemy.alive = False
                        bullet.active = False
                        score += 10
                        explosions.append(Explosion(enemy.x, enemy.y))
                        explosion_sound.play()
                        
                        # Chance to drop power-up
                        if random.random() < POWERUP_DROP_CHANCE:
                            power_type = random.choice(['double_shot', 'shield'])
                            power_ups.append(PowerUp(enemy.x, enemy.y, power_type))
                        break
        # Remove inactive bullets
        player_bullets = [b for b in player_bullets if b.active]

        # Check enemy bullet shooting: randomly let one alive enemy shoot
        alive_enemies = [enemy for enemy in enemies if enemy.alive]
        if alive_enemies and random.random() < ENEMY_SHOOT_PROB:
            shooter = random.choice(alive_enemies)
            enemy_bullets.append(EnemyBullet(shooter.x + shooter.width//2 - ENEMY_BULLET_WIDTH//2, shooter.y + shooter.height))

        # Update power-ups
        for power_up in power_ups:
            if power_up.active:
                power_up.update()
                if not spaceship.destroyed and power_up.rect.colliderect(spaceship.rect):
                    if power_up.type == 'double_shot':
                        spaceship.double_shot = True
                        spaceship.power_up_timer = POWERUP_DURATION
                    elif power_up.type == 'shield':
                        spaceship.shield = True
                        spaceship.power_up_timer = POWERUP_DURATION
                    power_up.active = False
        power_ups = [p for p in power_ups if p.active]

        # Update power-up timer
        if spaceship.power_up_timer > 0:
            spaceship.power_up_timer -= 1
            if spaceship.power_up_timer <= 0:
                spaceship.double_shot = False
                spaceship.shield = False

        # Update enemy bullets and check collision with spaceship
        for eb in enemy_bullets:
            if eb.active:
                eb.update()
                if not spaceship.destroyed and not spaceship.invulnerable and not spaceship.shield and eb.rect.colliderect(spaceship.rect):
                    spaceship.destroyed = True
                    explosions.append(Explosion(spaceship.x, spaceship.y))
                    explosion_sound.play()
                    spaceship.lives -= 1
                    if spaceship.lives <= 0:
                        game_over = True
                        game_over_sound.play()
                    else:
                        spaceship.respawn()
        enemy_bullets = [eb for eb in enemy_bullets if eb.active]

        # Spawn and update UFO
        if not ufo and random.random() < UFO_SPAWN_PROB:
            direction = random.choice([1, -1])
            if direction == 1:
                ufo = UFO(-60, direction)  # start off-screen left
            else:
                ufo = UFO(SCREEN_WIDTH, direction)  # start off-screen right
            ufo_sound.play()
        if ufo:
            ufo.update()

            # UFO shooting bullets
            if random.random() < UFO_SHOOT_PROB:
                enemy_bullets.append(EnemyBullet(ufo.x + ufo.rect.width//2 - ENEMY_BULLET_WIDTH//2, ufo.y + ufo.rect.height))

            # Check collision with player bullets
            for bullet in player_bullets:
                if bullet.active and bullet.rect.colliderect(ufo.rect):
                    bullet.active = False
                    explosions.append(Explosion(ufo.x, ufo.y))
                    explosion_sound.play()
                    score += UFO_BONUS_POINTS
                    ufo = None
                    break
            if ufo and not ufo.active:
                ufo = None

        # Update explosions and remove inactive ones
        for exp in explosions:
            exp.update()
        explosions = [exp for exp in explosions if exp.active]

        # Check for game over: if any enemy reaches close to spaceship
        for enemy in enemies:
            if enemy.alive and enemy.y + enemy.height >= spaceship.y:
                game_over = True
                break
        if all(not enemy.alive for enemy in enemies) and ufo is None:
            game_over = True

        # Draw everything
        screen.fill(BLACK)
        if not spaceship.destroyed:
            spaceship.draw(screen)
        # Draw player bullets
        for bullet in player_bullets:
            if bullet.active:
                bullet.draw(screen)
        for enemy in enemies:
            if enemy.alive:
                enemy.draw(screen)
        # Draw enemy bullets
        for eb in enemy_bullets:
            if eb.active:
                eb.draw(screen)
        # Draw UFO if it exists
        if ufo:
            ufo.draw(screen)
        # Draw explosions
        for exp in explosions:
            exp.draw(screen)

        # Display score and draw lives
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        draw_lives(screen, spaceship)

        # Draw power-ups
        for power_up in power_ups:
            power_up.draw(screen)

        # Display active power-ups
        if spaceship.double_shot:
            power_text = font.render('Double Shot!', True, (255, 255, 0))
            screen.blit(power_text, (SCREEN_WIDTH - 150, 10))
        if spaceship.shield:
            shield_text = font.render('Shield!', True, (0, 255, 255))
            screen.blit(shield_text, (SCREEN_WIDTH - 150, 40))

        # Create overlay surface for game over
        if game_over:
            # Handle high score first
            if not hasattr(spaceship, 'name_entered'):
                if is_high_score(score):
                    # Clear any remaining events before name input
                    pygame.event.clear()
                    player_name = get_player_name(screen, font)
                    save_high_score(score, player_name)
                spaceship.name_entered = True
            
            # Create semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)  # 200/255 opacity
            screen.blit(overlay, (0, 0))
            
            # Draw game over content
            y_offset = SCREEN_HEIGHT // 2 - 100
            msg = 'You Win!' if all(not enemy.alive for enemy in enemies) else 'Game Over!'
            game_over_text = font.render(msg, True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, y_offset))
            
            # Display score
            y_offset += 40
            final_score_text = font.render(f'Final Score: {score}', True, WHITE)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, y_offset))
            
            # Display high scores
            y_offset += 50
            high_score_text = font.render('High Scores:', True, WHITE)
            screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, y_offset))
            
            # Load fresh high scores each frame in case they changed
            high_scores = load_high_scores()
            for i, hs in enumerate(high_scores[:5]):
                y_offset += 30
                score_text = font.render(f'{i+1}. {hs["name"]}: {hs["score"]}', True, WHITE)
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_offset))
            
            # Display restart/quit instructions
            y_offset += 50
            restart_text = font.render('Press SPACE to Play Again or ESC to Quit', True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y_offset))
            
            # Handle input events for game over
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True  # Restart game
                    elif event.key == pygame.K_ESCAPE:
                        return False  # Quit game

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    while True:
        try:
            if not main():  # If main returns False, quit the game
                break
        except Exception as e:
            print(f"Error: {e}")
            break
    
    pygame.quit()
    sys.exit()
