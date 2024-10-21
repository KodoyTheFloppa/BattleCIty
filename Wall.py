import pygame

class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        # Реализовать отрисовку стены
        pygame.draw.rect(screen, (128, 128, 128), (self.x, self.y, 40, 40))