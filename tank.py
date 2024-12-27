from dataclasses import FrozenInstanceError

import pygame, random

from Timer import gtimer
from explosion import Explosion
from Bullet import Bullet
from Label import Label
import globals


class Tank:
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	(STATE_SPAWNING, STATE_DEAD, STATE_ALIVE, STATE_EXPLODING) = range(4)

	(SIDE_PLAYER, SIDE_ENEMY) = range(2)

	def __init__(self, level, side, position=None, direction=None):
		self.health = 100

		self.paralised = False

		self.paused = False

		self.shielded = False

		self.speed = 2

		self.max_active_bullets = 1

		self.side = side

		self.flash = 0

		self.superpowers = 0

		self.bonus = None

		self.controls = [pygame.K_SPACE, pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]

		self.pressed = [False] * 4

		self.shield_images = [
			globals.sprites.subsurface(0, 48 * 2, 16 * 2, 16 * 2),
			globals.sprites.subsurface(16 * 2, 48 * 2, 16 * 2, 16 * 2)
		]
		self.shield_image = self.shield_images[0]
		self.shield_index = 0

		self.spawn_images = [
			globals.sprites.subsurface(32 * 2, 48 * 2, 16 * 2, 16 * 2),
			globals.sprites.subsurface(48 * 2, 48 * 2, 16 * 2, 16 * 2)
		]
		self.spawn_image = self.spawn_images[0]
		self.spawn_index = 0

		self.level = level

		if position is not None:
			self.rect = pygame.Rect(position, (26, 26))
		else:
			self.rect = pygame.Rect(0, 0, 26, 26)

		if direction is None:
			self.direction = random.choice([self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT])
		else:
			self.direction = direction

		self.state = self.STATE_SPAWNING

		self.timer_uuid_spawn = gtimer.add(100, lambda: self.toggleSpawnImage())

		self.timer_uuid_spawn_end = gtimer.add(1000, lambda: self.endSpawning())

	def endSpawning(self):
		self.state = self.STATE_ALIVE
		gtimer.destroy(self.timer_uuid_spawn_end)

	def toggleSpawnImage(self):
		if self.state != self.STATE_SPAWNING:
			gtimer.destroy(self.timer_uuid_spawn)
			return
		self.spawn_index += 1
		if self.spawn_index >= len(self.spawn_images):
			self.spawn_index = 0
		self.spawn_image = self.spawn_images[self.spawn_index]

	def toggleShieldImage(self):
		if self.state != self.STATE_ALIVE:
			gtimer.destroy(self.timer_uuid_shield)
			return
		if self.shielded:
			self.shield_index += 1
			if self.shield_index >= len(self.shield_images):
				self.shield_index = 0
			self.shield_image = self.shield_images[self.shield_index]

	def draw(self):
		if self.state == self.STATE_ALIVE:
			globals.screen.blit(self.image, self.rect.topleft)
			if self.shielded:
				globals.screen.blit(self.shield_image, [self.rect.left - 3, self.rect.top - 3])
		elif self.state == self.STATE_EXPLODING:
			self.explosion.draw()
		elif self.state == self.STATE_SPAWNING:
			globals.screen.blit(self.spawn_image, self.rect.topleft)

	def explode(self):
		if self.state != self.STATE_DEAD:
			self.state = self.STATE_EXPLODING
			self.explosion = Explosion(self.rect.topleft)

			if self.bonus:
				self.spawnBonus()

	def fire(self, forced=False):
		if self.state != self.STATE_ALIVE:
			gtimer.destroy(self.timer_uuid_fire)
			return False

		if self.paused:
			return False

		if not forced:
			active_bullets = 0
			for bullet in globals.bullets:
				if bullet.owner_class == self and bullet.state == bullet.STATE_ACTIVE:
					active_bullets += 1
			if active_bullets >= self.max_active_bullets:
				return False

		bullet = Bullet(self.level, self.rect.topleft, self.direction)

		if self.superpowers > 0:
			bullet.speed = 8

		if self.superpowers > 2:
			bullet.power = 2

		if self.side == self.SIDE_PLAYER:
			bullet.owner = self.SIDE_PLAYER
		else:
			bullet.owner = self.SIDE_ENEMY
			self.bullet_queued = False

		bullet.owner_class = self
		globals.bullets.append(bullet)
		return True

	def rotate(self, direction, fix_position=True):
		self.direction = direction

		if direction == self.DIR_UP:
			self.image = self.image_up
		elif direction == self.DIR_RIGHT:
			self.image = self.image_right
		elif direction == self.DIR_DOWN:
			self.image = self.image_down
		elif direction == self.DIR_LEFT:
			self.image = self.image_left

		if fix_position:
			new_x = self.nearest(self.rect.left, 8) + 3
			new_y = self.nearest(self.rect.top, 8) + 3

			if abs(self.rect.left - new_x) < 5:
				self.rect.left = new_x

			if abs(self.rect.top - new_y) < 5:
				self.rect.top = new_y

	def turnAround(self):
		if self.direction in (self.DIR_UP, self.DIR_RIGHT):
			self.rotate(self.direction + 2, False)
		else:
			self.rotate(self.direction - 2, False)

	def update(self, time_passed):
		if self.state == self.STATE_EXPLODING:
			if not self.explosion.active:
				self.state = self.STATE_DEAD
				del self.explosion

	def nearest(self, num, base):
		return int(round(num / (base * 1.0)) * base)

	def bulletImpact(self, friendly_fire=False, damage=100, tank=None):
		if self.shielded:
			return True

		if not friendly_fire:
			self.health -= damage
			if self.health < 1:
				if self.side == self.SIDE_ENEMY:
					if globals.play_sounds:
						globals.sounds["explosion"].play()


				self.explode()
			return True

		if self.side == self.SIDE_ENEMY:
			return False
		elif self.side == self.SIDE_PLAYER:
			if not self.paralised:
				self.setParalised(True)
				self.timer_uuid_paralise = gtimer.add(10000, lambda: self.setParalised(False), 1)
			return True

	def setParalised(self, paralised=True):
		if self.state != self.STATE_ALIVE:
			gtimer.destroy(self.timer_uuid_paralise)
			return
		self.paralised = paralised
