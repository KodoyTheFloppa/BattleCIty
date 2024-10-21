import pygame
import random
from Tank import Tank, Explosion



class EnemyTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, image_name='EnemyTank.png')
        self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

    def update(self, tanks):
        # Случайное движение
        if random.random() < 0.05:  # 5% вероятность смены направления
            self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

        self.rotate(self.direction)
        self.move(tanks)

        # Проверка коллизий с пулями
        for bullet in self.bullets:
            if bullet.rect.colliderect(self.rect):
                self.explosions.append(Explosion(self.x, self.y))  # Взрыв
                self.bullets.remove(bullet)  # Удалить пулю
                break