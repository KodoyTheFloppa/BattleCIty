import pygame
from Tank import Tank, Explosion


class PlayerTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, image_name='PlayerTank.png')

    def update(self, tanks):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rotate('UP')
            self.move(tanks)
        elif keys[pygame.K_DOWN]:
            self.rotate('DOWN')
            self.move(tanks)
        elif keys[pygame.K_LEFT]:
            self.rotate('LEFT')
            self.move(tanks)
        elif keys[pygame.K_RIGHT]:
            self.rotate('RIGHT')
            self.move(tanks)
        if keys[pygame.K_SPACE]:
            self.shoot()

        # Обновление взрывов и коллизий с пулями
        for bullet in self.bullets:
            bullet.move()
            if bullet.rect.colliderect(self.rect):
                self.explosions.append(Explosion(self.x, self.y))  # Взрыв
                self.bullets.remove(bullet)  # Удалить пулю
                break