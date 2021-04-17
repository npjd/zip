import pygame
from pygame import mixer
import os
import random
import csv

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.health = 100
        self.shoot_cooldown = 0
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        animation_types = ['idle', 'run', 'jump']