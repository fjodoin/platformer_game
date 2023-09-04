import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer") # Set caption at the top of the display

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH,HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    # For loop to load individual sprite sheets, iterate through, and transform if necessary
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() # Load an image from the available sprites, and add a transparent background
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0 , width, height)
            surface.blit(sprite_sheet, (0, 0), rect)           
            sprites.append(pygame.transform.scale2x(surface))       # x2 size of sprites
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    
    return all_sprites

class Player(pygame.sprite.Sprite):         # pygame.sprite.Sprite allows for easy collision perfect detection
    COLOR = (255, 0, 0)
    GRAVITY = 0
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)    # Spawn player sprite!
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps):
        # Loop will be called once every frame and perform animation (moving, jumping, etc.)
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)        # using "min with 1" so that gravity kicks in at 0 seconds, instead of 1 second.
        self.move(self.x_vel, self.y_vel)
        
        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.x_vel != 0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)    # Dynamic for any sprite_sheet!
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update():
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite) # Allows for pixel perfect collision! If we dont do this, is will be stuck with rectangular hit boxes that are not true to animation

    def draw(self, win):
        # self.sprite = self.SPRITES["idle_" + self.direction][0]
        win.blit(self.sprite, (self.rect.x, self.rect.y))

# Create a backsplash for the background
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    # Compare screen with tile
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height +1):
            pos = (i * width, j * height)
            tiles.append(pos)
    return tiles, image

def draw(window, background, bg_image, player):
    for tile in background:
        window.blit(bg_image, tile)

    player.draw(window)
    pygame.display.update()

def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)

def main(window):
    # Event loops
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    player = Player(100, 100, 50, 50)
    run = True
    while run:
        clock.tick(FPS) # Ensures the while-loop only runs 60 FPS per tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        player.loop(FPS)
        handle_move(player)
        draw(window, background, bg_image, player)
    
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)