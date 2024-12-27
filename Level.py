import os
import pygame

import glb
import globals
from Timer import gtimer
from Window import myRect


class Level:
    (TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

    TILE_SIZE = 16

    def __init__(self, level_nr=None):
        self.max_active_enemies = 4

        tile_images = [
            pygame.Surface((8 * 2, 8 * 2)),
            globals.sprites.subsurface(48 * 2, 64 * 2, 8 * 2, 8 * 2),
            globals.sprites.subsurface(48 * 2, 72 * 2, 8 * 2, 8 * 2),
            globals.sprites.subsurface(56 * 2, 72 * 2, 8 * 2, 8 * 2),
            globals.sprites.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2),
            globals.sprites.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2),
            globals.sprites.subsurface(72 * 2, 64 * 2, 8 * 2, 8 * 2),
            globals.sprites.subsurface(64 * 2, 72 * 2, 8 * 2, 8 * 2)
        ]
        self.tile_empty = tile_images[0]
        self.tile_brick = tile_images[1]
        self.tile_steel = tile_images[2]
        self.tile_grass = tile_images[3]
        self.tile_water = tile_images[4]
        self.tile_water1 = tile_images[4]
        self.tile_water2 = tile_images[5]
        self.tile_froze = tile_images[6]

        self.obstacle_rects = []

        level_nr = 1 if level_nr is None else level_nr % 10
        if level_nr == 0:
            level_nr = 10
        self.loadLevel(level_nr)

        self.obstacle_rects = []

        self.updateObstacleRects()

        gtimer.add(400, lambda: self.toggleWaves())

    def hitTile(self, pos, power=1, sound=False):
        for tile in self.mapr:
            if tile.topleft == pos:
                if tile.type == self.TILE_BRICK:
                    if globals.play_sounds and sound:
                        globals.sounds["brick"].play()
                    self.mapr.remove(tile)
                    self.updateObstacleRects()
                    return True
                elif tile.type == self.TILE_STEEL:
                    if globals.play_sounds and sound:
                        globals.sounds["steel"].play()
                    if power == 2:
                        self.mapr.remove(tile)
                        self.updateObstacleRects()
                    return True
                else:
                    return False

    def toggleWaves(self):
        if self.tile_water == self.tile_water1:
            self.tile_water = self.tile_water2
        else:
            self.tile_water = self.tile_water1

    def loadLevel(self, level_nr=1):
        filename = "levels/" + str(level_nr)
        if not os.path.isfile(filename):
            return False
        level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        self.mapr = []
        x, y = 0, 0
        for row in data:
            for ch in row:
                if ch == "#":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_BRICK))
                elif ch == "@":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_STEEL))
                elif ch == "~":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_WATER))
                elif ch == "%":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_GRASS))
                elif ch == "-":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_FROZE))
                x += self.TILE_SIZE
            x = 0
            y += self.TILE_SIZE
        return True

    def draw(self, tiles=None):
        for tile in self.mapr:
            if tile.type in tiles:
                if tile.type == self.TILE_BRICK:
                    globals.screen.blit(self.tile_brick, tile.topleft)
                elif tile.type == self.TILE_STEEL:
                    globals.screen.blit(self.tile_steel, tile.topleft)
                elif tile.type == self.TILE_WATER:
                    globals.screen.blit(self.tile_water, tile.topleft)
                elif tile.type == self.TILE_FROZE:
                    globals.screen.blit(self.tile_froze, tile.topleft)
                elif tile.type == self.TILE_GRASS:
                    globals.screen.blit(self.tile_grass, tile.topleft)

    def updateObstacleRects(self):
        self.obstacle_rects = [glb.castle.rect]

        for tile in self.mapr:
            if tile.type in (self.TILE_BRICK, self.TILE_STEEL, self.TILE_WATER):
                self.obstacle_rects.append(tile)

    def buildFortress(self, tile):
        positions = [
            (11 * self.TILE_SIZE, 23 * self.TILE_SIZE),
            (11 * self.TILE_SIZE, 24 * self.TILE_SIZE),
            (11 * self.TILE_SIZE, 25 * self.TILE_SIZE),
            (14 * self.TILE_SIZE, 23 * self.TILE_SIZE),
            (14 * self.TILE_SIZE, 24 * self.TILE_SIZE),
            (14 * self.TILE_SIZE, 25 * self.TILE_SIZE),
            (12 * self.TILE_SIZE, 23 * self.TILE_SIZE),
            (13 * self.TILE_SIZE, 23 * self.TILE_SIZE)
        ]

        obsolete = []

        for i, rect in enumerate(self.mapr):
            if rect.topleft in positions:
                obsolete.append(rect)
        for rect in obsolete:
            self.mapr.remove(rect)

        for pos in positions:
            self.mapr.append(myRect(pos[0], pos[1], self.TILE_SIZE, self.TILE_SIZE, tile))

        self.updateObstacleRects()
