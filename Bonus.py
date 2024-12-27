import pygame
import random

import globals


class Bonus:
	(BONUS_GRENADE, BONUS_HELMET, BONUS_SHOVEL, BONUS_STAR, BONUS_TANK, BONUS_TIMER) = range(6)

	def __init__(self, level):
		self.level = level

		self.active = True

		self.visible = True

		self.rect = pygame.Rect(random.randint(0, 416 - 32), random.randint(0, 416 - 32), 32, 32)

		self.bonus = random.choice([
			self.BONUS_GRENADE,
			self.BONUS_HELMET,
			self.BONUS_SHOVEL,
			self.BONUS_STAR,
			self.BONUS_TANK,
			self.BONUS_TIMER
		])

		self.image = globals.sprites.subsurface(16 * 2 * self.bonus, 32 * 2, 16 * 2, 15 * 2)

	def draw(self):
		if self.visible:
			globals.screen.blit(self.image, self.rect.topleft)

	def toggleVisibility(self):
		self.visible = not self.visible
