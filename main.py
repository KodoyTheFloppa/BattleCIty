import os, pygame, time, random, uuid, sys
from imports import *

if __name__ == "__main__":

	gtimer = Timer()

	sprites = None
	screen = None
	players = []
	enemies = []
	bullets = []
	bonuses = []
	labels = []

	play_sounds = True
	sounds = {}

	game = Game()
	castle = Castle()
	game.showMenu()