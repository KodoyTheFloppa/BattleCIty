import pygame
import os
from Settings import upscale

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 3
        self.image = upscale(pygame.image.load(os.path.join('Sprites', 'Bullet.png')), 3)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move(self):
        if self.direction == 'UP':
            self.y -= self.speed
        elif self.direction == 'DOWN':
            self.y += self.speed
        elif self.direction == 'LEFT':
            self.x -= self.speed
        elif self.direction == 'RIGHT':
            self.x += self.speed

        self.rect.topleft = (self.x, self.y)  # Обновление прямоугольника для коллизий

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))