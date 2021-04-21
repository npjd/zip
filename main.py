import pygame 
from pygame import mixer
import os
import random
import csv

pygame.init()
clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * .8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GRAVITY = 0.50
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
screen_scroll = 0
bg_scroll = 0
moving_left = False
moving_right = False
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    img_list.append(img)

cursor = pygame.transform.scale(pygame.image.load("img/temp_cursor.jpeg"), (50, 50))
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

def draw_bg():
    screen.fill((144, 201, 120))
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        self.image = cursor
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()
    def draw(self):
        screen.blit(self.image, self.rect)
    def update(self):
        self.rect.center = pygame.mouse.get_pos()

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,scale,ammo,weapon):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.ammo = ammo
        self.speed = 10
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 0
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        animation_types = ['idle','run','jump']
        for animation in animation_types:
            temp_list = []
            num_frame = len(os.listdir(f'img/player/{animation}'))
            for i in range(num_frame):
                img = pygame.image.load(f'img/player/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if self.jump is True and self.in_air is False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        self.vel_y += GRAVITY
        if self.vel_y >10:
            self.vel_y
        dy += self.vel_y

        

        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            dx = 0
        self.rect.x +=dx
        self.rect.y +=dy

        #scroll
        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x-=dx
            screen_scroll = -dx
        return screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 240
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time> ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index =0
    
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def update(self):
        self.update_animation()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class World():
    def __init__(self):
        self.obstacle_list = []
        
    def process_data(self, data):
        self.level_length = len(data[0])
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile == 15:#create player
                        player = Player( x * TILE_SIZE, y * TILE_SIZE, 3, 20, 5)
                        # health_bar = HealthBar(10, 10, player.health, player.health)
        return player


    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'world.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
cursor = Cursor()
player = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)
    draw_bg()
    cursor.draw()
    cursor.update()
    if cursor.rect.centerx < player.rect.centerx:
        player.flip = True
    else:
        player.flip = False
    world.draw()
    player.update()
    player.draw()
    if player.in_air:
        player.update_action(2)
    elif moving_left or moving_right:
        player.update_action(1)
    else:
        player.update_action(0)
    screen_scroll = player.move(moving_left, moving_right)
    bg_scroll -= screen_scroll
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
		#keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    pygame.display.update()

pygame.quit()
    