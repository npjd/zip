import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640

BOT_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN,SCREEN_HEIGHT + BOT_MARGIN))
pygame.display.set_caption("Map Maker")



run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()