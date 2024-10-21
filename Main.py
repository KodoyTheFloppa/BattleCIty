import pygame
from TankPlayer import PlayerTank
from TankEnemy import EnemyTank
from Settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Battle City')

    player_tank = PlayerTank(x=100, y=100)
    enemy_tank = EnemyTank(x=400, y=300)

    tanks = [player_tank, enemy_tank]

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(FPS)  # Время в миллисекундах
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновление состояния танков
        for tank in tanks:
            tank.update(tanks)

        # Обновление взрывов
        for tank in tanks:
            tank.update_explosions()

        screen.fill((0, 0, 0))  # Черный фон

        # Отрисовка танков
        for tank in tanks:
            tank.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()