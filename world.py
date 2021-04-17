import pygame
from pygame import mixer
import os
import random
import csv

class World():
	def __init__(self):
		self.obstacle_list = []
        