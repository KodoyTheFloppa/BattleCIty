import pygame

from tank import Tank
import globals


class Player(Tank):

	def __init__(self, level, type, position=None, direction=None, filename=None):
		Tank.__init__(self, level, type, position=None, direction=None)

		if filename is None:
			filename = (0, 0, 16 * 2, 16 * 2)

		self.start_position = position
		self.start_direction = direction

		self.lives = 3

		self.score = 0

		self.trophies = {
			"bonus": 0,
			"enemy0": 0,
			"enemy1": 0,
			"enemy2": 0,
			"enemy3": 0
		}

		self.image = globals.sprites.subsurface(filename)
		self.image_up = self.image
		self.image_left = pygame.transform.rotate(self.image, 90)
		self.image_down = pygame.transform.rotate(self.image, 180)
		self.image_right = pygame.transform.rotate(self.image, 270)

		if direction is None:
			self.rotate(self.DIR_UP, False)
		else:
			self.rotate(direction, False)

	def move(self, direction):
		if self.state == self.STATE_EXPLODING:
			if not self.explosion.active:
				self.state = self.STATE_DEAD
				del self.explosion

		if self.state != self.STATE_ALIVE:
			return

		if self.direction != direction:
			self.rotate(direction)

		if self.paralised:
			return

		if direction == self.DIR_UP:
			new_position = [self.rect.left, self.rect.top - self.speed]
			if new_position[1] < 0:
				return
		elif direction == self.DIR_RIGHT:
			new_position = [self.rect.left + self.speed, self.rect.top]
			if new_position[0] > (416 - 26):
				return
		elif direction == self.DIR_DOWN:
			new_position = [self.rect.left, self.rect.top + self.speed]
			if new_position[1] > (416 - 26):
				return
		elif direction == self.DIR_LEFT:
			new_position = [self.rect.left - self.speed, self.rect.top]
			if new_position[0] < 0:
				return

		player_rect = pygame.Rect(new_position, [26, 26])

		if player_rect.collidelist(self.level.obstacle_rects) != -1:
			return

		for player in globals.players:
			if player != self and player.state == player.STATE_ALIVE and player_rect.colliderect(player.rect) == True:
				return

		for enemy in globals.enemies:
			if player_rect.colliderect(enemy.rect):
				return

		for bonus in globals.bonuses:
			if player_rect.colliderect(bonus.rect):
				self.bonus = bonus

		self.rect.topleft = (new_position[0], new_position[1])

	def reset(self):
		self.rotate(self.start_direction, False)
		self.rect.topleft = self.start_position
		self.superpowers = 0
		self.max_active_bullets = 1
		self.health = 100
		self.paralised = False
		self.paused = False
		self.pressed = [False] * 4
		self.state = self.STATE_ALIVE
