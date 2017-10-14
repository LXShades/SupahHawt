import pygame

import time
import math
import random

# Declare globals
game_speed = 0.0

world_width = 1920
world_height = 1080

frame_time = time.clock()

background_colour = pygame.Color(255, 255, 255)
enemy_colour = pygame.Color(127, 0, 0)
player_colour = pygame.Color(0, 0, 255)
bullet_colour = pygame.Color(255, 0, 0)
score_area_colour = pygame.Color(0, 0, 0)
score_text_colour = pygame.Color(255, 255, 255)


class Player:
    x = 0
    y = 0
    size = 18
    centre_x = size / 2
    centre_y = size / 2
    max_speed = 200
    x_speed = 0
    y_speed = 0
    acceleration = 500
    friction = 800
    distance_threshold = 50
    sprite = None
    radius_sprite = None
    score = 0
    score_multiplier = 0
    high_score = 0
    mouse_mode = False

    def __init__(self):
        self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA, 32)
        self.sprite.fill(player_colour)
        self.radius_sprite = pygame.Surface((100, 100), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.radius_sprite, pygame.Color(127, 127, 127, 127), (50, 50), 50)

        self.x = random.randint(0, world_width)
        self.y = random.randint(0, world_height)

    def Update(self):
        global game_speed
        global delta_time
        global bullets
        last_x = self.x
        last_y = self.y

        # Adjust speed
        unit_x = 0
        unit_y = 0
        if pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]:
            unit_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]:
            unit_y += 1
        if pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]:
            unit_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]:
            unit_x += 1

        if unit_x != 0 or unit_y != 0:
            # Avoid Pythagorian blarghblaeeueugh movement speed glitch
            scale = distance(0, 0, unit_x, unit_y)
            unit_x /= scale
            unit_y /= scale
        else:
            # Friction
            cur_total_speed = distance(0, 0, self.x_speed, self.y_speed)
            if cur_total_speed > self.friction * delta_time:
                self.x_speed -= self.x_speed * self.friction * delta_time / cur_total_speed
                self.y_speed -= self.y_speed * self.friction * delta_time / cur_total_speed
            else:
                self.x_speed = 0
                self.y_speed = 0

        self.x_speed += unit_x * self.acceleration * delta_time
        self.y_speed += unit_y * self.acceleration * delta_time

        # Cap speed
        cur_total_speed = distance(0, 0, self.x_speed, self.y_speed)
        if cur_total_speed > self.max_speed:
            self.x_speed *= self.max_speed / cur_total_speed
            self.y_speed *= self.max_speed / cur_total_speed
            cur_total_speed = self.max_speed

        # Move player
        self.x += self.x_speed * delta_time
        self.y += self.y_speed * delta_time

        # If mouse mode, never mind all that (test)
        if self.mouse_mode:
            self.x = pygame.mouse.get_pos()[0] - self.centre_x
            self.y = pygame.mouse.get_pos()[1] - self.centre_y
            cur_total_speed = distance(last_x, last_y, self.x, self.y) / delta_time

        # Update global game speed in response
        game_speed = cur_total_speed / self.max_speed
        if game_speed < 0.1:
            game_speed = 0.1

        # Update score based on proximity to bullets
        num_close_bullets = 0
        for bullet in bullets:
            if distance(self.x, self.y, bullet.x, bullet.y) < self.distance_threshold:
                num_close_bullets += 1

        for bullet in bullets:
            dist = distance(self.x, self.y, bullet.x, bullet.y)
            if dist < self.distance_threshold:
                self.score += (self.distance_threshold - dist) * num_close_bullets * game_speed * delta_time

        self.score_multiplier = num_close_bullets
        if self.score > self.high_score:
            self.high_score = self.score

        # If collision with bullets occurs, penalise score
        for bullet in bullets:
            if bullet.x >= self.x and bullet.x < self.x + self.size and \
                    bullet.y >= self.y and bullet.y < self.y + self.size:
                bullets.remove(bullet)
                self.score = 0

    def Draw(self):
        spr =  pygame.transform.scale(self.radius_sprite, (self.distance_threshold * 2, self.distance_threshold * 2))
        screen.blit(spr, (self.x - self.distance_threshold / 2, self.y - self.distance_threshold / 2))
        screen.blit(self.sprite, (self.x, self.y))

    def OnClick(self):
        self.mouse_mode = not self.mouse_mode

class Bullet:
    x = 0.0
    y = 0.0
    size = 5
    speed = 70
    centre_x = 2.5
    centre_y = 2.5
    trajectory = 0  # in radians

    def __init__(self, x, y, trajectory):
        self.x = float(x)
        self.y = float(y)
        self.trajectory = trajectory

    def Draw(self):
        if distance(player.x, player.y, self.x, self.y) < player.distance_threshold:
            if int(frame_time * 30.0) % 2:
                return  # Blink effect

        screen.blit(bullet_sprite, (self.x - self.size / 2, self.y - self.size / 2))

    def Update(self):
        global game_speed
        global delta_time
        global bullets
        self.x += math.cos(self.trajectory) * self.speed * game_speed * delta_time
        self.y += math.sin(self.trajectory) * self.speed * game_speed * delta_time

        if self.x < 0 or self.x >= world_width or self.y < 0 or self.y >= world_height:
            bullets.remove(self)

class Enemy:
    x = 0
    y = 0
    centre_x = 10
    centre_y = 10
    shot_timer = 1

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def Update(self):
        global game_speed
        global bullets
        global player
        self.shot_timer -= game_speed * delta_time

        if self.shot_timer < 0:
            bullets.append(Bullet(self.x, self.y, direction(self.x, self.y, player.x, player.y)))
            self.shot_timer = 1.0

    def Draw(self):
        screen.blit(enemy_sprite, (self.x - self.centre_x, self.y - self.centre_y))

def distance(x1, y1, x2, y2):
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))

def direction(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)

# Initialise
pygame.init()
screen = pygame.display.set_mode((world_width, world_height))

# Create objects and player(s)
player = Player()
bullets = list()
enemies = list()

for i in xrange(0, 20):
    enemies.append(Enemy(random.randint(0, world_width), random.randint(0, world_height)))

bullet_sprite = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
bullet_sprite.fill((0, 0, 0, 0))
pygame.draw.circle(bullet_sprite, bullet_colour, (5, 5), 5)

enemy_sprite = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
enemy_sprite.fill((0, 0, 0, 0))
pygame.draw.rect(enemy_sprite, enemy_colour, pygame.Rect(0, 5, 20, 10), 5)
font = pygame.font.SysFont("Ariel", 32)

# Main loop
running = True
while running:
    # Update game time
    last_time = frame_time
    frame_time = time.clock()
    delta_time = frame_time - last_time

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.OnClick()

    # Update game scene
    player.Update()

    for bullet in bullets:
        bullet.Update()
    for enemy in enemies:
        enemy.Update()

    # Render
    screen.fill(background_colour)

    for bullet in bullets:
        bullet.Draw()
    for enemy in enemies:
        enemy.Draw()

    player.Draw()

    # UI
    pygame.draw.rect(screen, score_area_colour, pygame.Rect(0, 0, world_width, font.get_height() * 1.10))
    text = font.render("Score: " + str(int(player.score)), True, score_text_colour)
    text2 = font.render("Multiplier: " + str(player.score_multiplier), True, score_text_colour)
    text3 = font.render("High Score: " + str(int(player.high_score)), True, score_text_colour)
    screen.blit(text, (0, 0))
    screen.blit(text2, (world_width * 0.33, 0))
    screen.blit(text3, (world_width * 0.66, 0))

    # Flip to display!
pygame.display.flip()