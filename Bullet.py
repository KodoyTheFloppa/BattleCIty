import pygame
from explosion import Explosion
import globals
import glb


class Bullet:
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	(STATE_REMOVED, STATE_ACTIVE, STATE_EXPLODING) = range(3)

	(OWNER_PLAYER, OWNER_ENEMY) = range(2)

	def __init__(self, level, position, direction, damage=100, speed=5):
		self.level = level
		self.direction = direction
		self.damage = damage
		self.owner = None
		self.owner_class = None

		self.power = 1

		self.image = globals.sprites.subsurface(75 * 2, 74 * 2, 3 * 2, 4 * 2)

		if direction == self.DIR_UP:
			self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
		elif direction == self.DIR_RIGHT:
			self.image = pygame.transform.rotate(self.image, 270)
			self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
		elif direction == self.DIR_DOWN:
			self.image = pygame.transform.rotate(self.image, 180)
			self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
		elif direction == self.DIR_LEFT:
			self.image = pygame.transform.rotate(self.image, 90)
			self.rect = pygame.Rect(position[0] - 8, position[1] + 11, 8, 6)

		self.explosion_images = [
			globals.sprites.subsurface(0, 80 * 2, 32 * 2, 32 * 2),
			globals.sprites.subsurface(32 * 2, 80 * 2, 32 * 2, 32 * 2),
		]

		self.speed = speed

		self.state = self.STATE_ACTIVE

	def draw(self):
		if self.state == self.STATE_ACTIVE:
			globals.screen.blit(self.image, self.rect.topleft)
		elif self.state == self.STATE_EXPLODING:
			self.explosion.draw()

	def update(self):

		if self.state == self.STATE_EXPLODING:
			if not self.explosion.active:
				self.destroy()
				del self.explosion

		if self.state != self.STATE_ACTIVE:
			return

		if self.direction == self.DIR_UP:
			self.rect.topleft = [self.rect.left, self.rect.top - self.speed]
			if self.rect.top < 0:
				if globals.play_sounds and self.owner == self.OWNER_PLAYER:
					globals.sounds["steel"].play()
				self.explode()
				return
		elif self.direction == self.DIR_RIGHT:
			self.rect.topleft = [self.rect.left + self.speed, self.rect.top]
			if self.rect.left > (416 - self.rect.width):
				if globals.play_sounds and self.owner == self.OWNER_PLAYER:
					globals.sounds["steel"].play()
				self.explode()
				return
		elif self.direction == self.DIR_DOWN:
			self.rect.topleft = [self.rect.left, self.rect.top + self.speed]
			if self.rect.top > (416 - self.rect.height):
				if globals.play_sounds and self.owner == self.OWNER_PLAYER:
					globals.sounds["steel"].play()
				self.explode()
				return
		elif self.direction == self.DIR_LEFT:
			self.rect.topleft = [self.rect.left - self.speed, self.rect.top]
			if self.rect.left < 0:
				if globals.play_sounds and self.owner == self.OWNER_PLAYER:
					globals.sounds["steel"].play()
				self.explode()
				return

		has_collided = False

		rects = self.level.obstacle_rects
		collisions = self.rect.collidelistall(rects)
		if collisions:
			for i in collisions:
				if self.level.hitTile(rects[i].topleft, self.power, self.owner == self.OWNER_PLAYER):
					has_collided = True
		if has_collided:
			self.explode()
			return

		for bullet in globals.bullets:
			if self.state == self.STATE_ACTIVE and bullet.owner != self.owner and bullet != self and self.rect.colliderect(
					bullet.rect):
				self.destroy()
				self.explode()
				return

		for player in globals.players:
			if player.state == player.STATE_ALIVE and self.rect.colliderect(player.rect):
				if player.bulletImpact(self.owner == self.OWNER_PLAYER, self.damage, self.owner_class):
					self.destroy()
					return

		for enemy in globals.enemies:
			if enemy.state == enemy.STATE_ALIVE and self.rect.colliderect(enemy.rect):
				if enemy.bulletImpact(self.owner == self.OWNER_ENEMY, self.damage, self.owner_class):
					self.destroy()
					return

		if glb.castle.active and self.rect.colliderect(glb.castle.rect):
			glb.castle.destroy()
			self.destroy()
			return

	def explode(self):
		if self.state != self.STATE_REMOVED:
			self.state = self.STATE_EXPLODING
			self.explosion = Explosion([self.rect.left - 13, self.rect.top - 13], None, self.explosion_images)

	def destroy(self):
		self.state = self.STATE_REMOVED
