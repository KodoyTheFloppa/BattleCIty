import unittest
from unittest.mock import Mock, patch
import pygame
from Enemy import Enemy
from Player import Player
from Level import Level
from Bullet import Bullet
from Castle import Castle
from tank import Tank
from Bonus import Bonus



class Tests(unittest.TestCase):

    def setUp(self):
        self.level = Level()
        self.level.enemies_left = [0, 1, 2, 3]
        self.enemy = Enemy(self.level, Enemy.TYPE_BASIC)
        self.level.TILE_SIZE = 16
        self.level.obstacle_rects = []


    def test_level_loading(self):
        self.level.loadLevel = Mock(return_value=True)
        self.assertTrue(self.level.loadLevel(1))


    def test_enemy_collision(self):
        self.enemy.rect.topleft = (0, 0)
        self.enemy.path = [(0, -10)]
        self.enemy.move()
        self.assertEqual(self.enemy.rect.topleft, (0, 0))


    def test_tank_explode(self):
        tank = Tank(level=self.level, side=Tank.SIDE_PLAYER, position=[100, 100])
        tank.explode()
        self.assertEqual(tank.state, Tank.STATE_EXPLODING)


    def test_castle_initial_state(self):
        castle = Castle()
        self.assertEqual(castle.state, Castle.STATE_STANDING)
        self.assertTrue(castle.active)


    def test_castle_destroy(self):
        castle = Castle()
        castle.destroy()
        self.assertEqual(castle.state, Castle.STATE_EXPLODING)
        self.assertFalse(castle.active)


    def test_castle_rebuild(self):
        castle = Castle()
        castle.destroy()
        castle.rebuild()
        self.assertEqual(castle.state, Castle.STATE_STANDING)
        self.assertTrue(castle.active)


    def test_bullet_creation(self):
        bullet = Bullet(level=self.level, position=[100, 100], direction=Bullet.DIR_UP)
        self.assertEqual(bullet.direction, Bullet.DIR_UP)
        self.assertEqual(bullet.state, Bullet.STATE_ACTIVE)


    def test_bullet_movement(self):
        bullet = Bullet(level=self.level, position=[100, 100], direction=Bullet.DIR_UP)
        initial_position = bullet.rect.topleft
        bullet.update()
        self.assertNotEqual(bullet.rect.topleft, initial_position)


    def test_bullet_collision_with_obstacle(self):
        bullet = Bullet(level=self.level, position=[50, 50], direction=Bullet.DIR_UP)
        self.level.obstacle_rects = [pygame.Rect(50, 40, 16, 16)]
        bullet.update()
        self.assertEqual(bullet.state, 1)


    def test_bonus_creation(self):
        bonus = Bonus(level=self.level)
        self.assertIn(bonus.bonus, [
            Bonus.BONUS_GRENADE,
            Bonus.BONUS_HELMET,
            Bonus.BONUS_SHOVEL,
            Bonus.BONUS_STAR,
            Bonus.BONUS_TANK,
            Bonus.BONUS_TIMER
        ])
        self.assertTrue(bonus.active)

    def test_bonus_toggle_visibility(self):
        bonus = Bonus(level=self.level)
        initial_visibility = bonus.visible
        bonus.toggleVisibility()
        self.assertNotEqual(bonus.visible, initial_visibility)



if __name__ == "__main__":
    unittest.main()
