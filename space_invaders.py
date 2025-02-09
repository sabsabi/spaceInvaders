import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

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
UFO_SPAWN_PROB = 0.005
UFO_BONUS_POINTS = 150
UFO_SHOOT_PROB = 0.005

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
class Spaceship:
    def __init__(self):
        self.width = SHIP_WIDTH
        self.height = SHIP_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = SHIP_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Load and resize spaceship image
        self.image = pygame.transform.scale(pygame.image.load('sprites/ship.png'), (SHIP_WIDTH, SHIP_HEIGHT))

    def move(self, dx):
        self.x += dx * self.speed
        # Keep the spaceship within the screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        self.rect.x = self.x

    def draw(self, surface):
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
        # Load and resize enemy image
        self.image = pygame.transform.scale(pygame.image.load('sprites/enemy.png'), (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.alive = True

    def update(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

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
def main():
    spaceship = Spaceship()
    bullet = None
    enemies = create_enemies(5, 10)
    enemy_bullets = []
    explosions = []
    ufo = None
    enemy_dx = ENEMY_SPEED
    enemy_move_down = False

    score = 0
    font = pygame.font.SysFont(None, 36)
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Fire bullet when space is pressed and there's no active bullet
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE and (bullet is None or not bullet.active):
                    # Bullet starts at the middle top of the spaceship
                    bullet = Bullet(spaceship.x + spaceship.width // 2 - BULLET_WIDTH // 2, spaceship.y)
            
        keys = pygame.key.get_pressed()
        if not game_over:
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

        # Update bullet and check for collisions
        if bullet and bullet.active:
            bullet.update()
            # Check collision with enemies
            for enemy in enemies:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    enemy.alive = False
                    bullet.active = False
                    score += 10
                    explosions.append(Explosion(enemy.x, enemy.y))
                    break

        # Check enemy bullet shooting: randomly let one alive enemy shoot
        alive_enemies = [enemy for enemy in enemies if enemy.alive]
        if alive_enemies and random.random() < ENEMY_SHOOT_PROB:
            shooter = random.choice(alive_enemies)
            enemy_bullets.append(EnemyBullet(shooter.x + shooter.width//2 - ENEMY_BULLET_WIDTH//2, shooter.y + shooter.height))

        # Update enemy bullets and check collision with spaceship
        for eb in enemy_bullets:
            if eb.active:
                eb.update()
                if eb.rect.colliderect(spaceship.rect):
                    explosions.append(Explosion(spaceship.x, spaceship.y, permanent=True))
                    game_over = True
        enemy_bullets = [eb for eb in enemy_bullets if eb.active]

        # Spawn and update UFO
        if not ufo and random.random() < UFO_SPAWN_PROB:
            direction = random.choice([1, -1])
            if direction == 1:
                ufo = UFO(-60, direction)  # start off-screen left
            else:
                ufo = UFO(SCREEN_WIDTH, direction)  # start off-screen right
        if ufo:
            ufo.update()

            # UFO shooting bullets
            if random.random() < UFO_SHOOT_PROB:
                enemy_bullets.append(EnemyBullet(ufo.x + ufo.rect.width//2 - ENEMY_BULLET_WIDTH//2, ufo.y + ufo.rect.height))

            # Check collision with spaceship bullet
            if bullet and bullet.active and bullet.rect.colliderect(ufo.rect):
                bullet.active = False
                explosions.append(Explosion(ufo.x, ufo.y))
                score += UFO_BONUS_POINTS
                ufo = None
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
        spaceship.draw(screen)
        if bullet and bullet.active:
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

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Display game over message if needed
        if game_over:
            msg = "You Win!" if all(not enemy.alive for enemy in enemies) else "Game Over!"
            game_over_text = font.render(msg, True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                          SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
