import pygame
import os
from Settings import upscale
from Settings import SCREEN_WIDTH, SCREEN_HEIGHT
from Bullet import Bullet

class Tank:
    def __init__(self, x, y, image_name):
        self.x = x
        self.y = y
        self.original_image = upscale(pygame.image.load(os.path.join('Sprites', image_name)), 3)
        self.image = self.original_image
        self.direction = 'UP'
        self.speed = 2
        self.bullets = []  # Список пуль
        self.explosions = []  # Список взрывов
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move(self, tanks):
        # Обновление прямоугольника для коллизий
        self.rect.topleft = (self.x, self.y)
        # Проверка выхода за границы экрана
        if self.direction == 'UP' and self.y > 0:
            self.y -= self.speed
        elif self.direction == 'DOWN' and self.y < SCREEN_HEIGHT - self.rect.height:
            self.y += self.speed
        elif self.direction == 'LEFT' and self.x > 0:
            self.x -= self.speed
        elif self.direction == 'RIGHT' and self.x < SCREEN_WIDTH - self.rect.width:
            self.x += self.speed

        # Проверка коллизий с другими танками
        for tank in tanks:
            if tank != self and self.rect.colliderect(tank.rect):
                if self.direction == 'UP':
                    self.y += self.speed
                elif self.direction == 'DOWN':
                    self.y -= self.speed
                elif self.direction == 'LEFT':
                    self.x += self.speed
                elif self.direction == 'RIGHT':
                    self.x -= self.speed

    def shoot(self):
        # Установка координат пули перед танком в зависимости от направления
        if self.direction == 'UP':
            bullet_x = self.x + self.rect.width // 2
            bullet_y = self.y
        elif self.direction == 'DOWN':
            bullet_x = self.x + self.rect.width // 2
            bullet_y = self.y + self.rect.height
        elif self.direction == 'LEFT':
            bullet_x = self.x
            bullet_y = self.y + self.rect.height // 2
        else:
            bullet_x = self.x + self.rect.width
            bullet_y = self.y + self.rect.height // 2

        bullet = Bullet(bullet_x, bullet_y, self.direction)
        self.bullets.append(bullet)

    def rotate(self, new_direction):
        self.direction = new_direction
        if self.direction == 'UP':
            self.image = self.original_image
        elif self.direction == 'DOWN':
            self.image = pygame.transform.rotate(self.original_image, 180)
        elif self.direction == 'LEFT':
            self.image = pygame.transform.rotate(self.original_image, 90)
        elif self.direction == 'RIGHT':
            self.image = pygame.transform.rotate(self.original_image, -90)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(screen)
        for explosion in self.explosions:
            explosion.draw(screen)

    def update_explosions(self):
        # Удаляем взрывы, которые закончились
        self.explosions = [explosion for explosion in self.explosions if explosion.active]

class Explosion:
    def __init__(self, x, y):
        self.images = [
            pygame.image.load(os.path.join('Sprites', 'TankExplosion1.png')),
            pygame.image.load(os.path.join('Sprites', 'TankExplosion2.png')),
            pygame.image.load(os.path.join('Sprites', 'TankExplosion3.png')),
            pygame.image.load(os.path.join('Sprites', 'TankExplosion4.png')),
        ]
        self.index = 0
        self.x = x
        self.y = y
        self.image = self.images[self.index]
        self.active = True
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= 500:  # 0.5 секунды для каждого изображения
            self.timer = 0
            self.index += 1
            if self.index < len(self.images):
                self.image = self.images[self.index]
            else:
                self.active = False  # Взрыв закончен

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))