import pygame


sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 224])
screen = None
players = []
enemies = []
bullets = []
bonuses = []
labels = []

play_sounds = False
sounds = {}
