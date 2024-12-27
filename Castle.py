import pygame
from explosion import Explosion
import globals


class Castle:
	(STATE_STANDING, STATE_DESTROYED, STATE_EXPLODING) = range(3)

	def __init__(self):
		self.img_undamaged = globals.sprites.subsurface(0, 15 * 2, 16 * 2, 16 * 2)
		self.img_destroyed = globals.sprites.subsurface(16 * 2, 15 * 2, 16 * 2, 16 * 2)

		self.rect = pygame.Rect(12 * 16, 24 * 16, 32, 32)

		self.rebuild()

	def draw(self):
		globals.screen.blit(self.image, self.rect.topleft)

		if self.state == self.STATE_EXPLODING:
			if not self.explosion.active:
				self.state = self.STATE_DESTROYED
				del self.explosion
			else:
				self.explosion.draw()

	def rebuild(self):
		self.state = self.STATE_STANDING
		self.image = self.img_undamaged
		self.active = True

	def destroy(self):
		self.state = self.STATE_EXPLODING
		self.explosion = Explosion(self.rect.topleft)
		self.image = self.img_destroyed
		self.active = False
