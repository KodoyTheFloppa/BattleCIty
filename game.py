import os, pygame, random, sys
from Timer import gtimer
from Castle import Castle
from Label import Label
from Enemy import Enemy
from Player import Player
from Level import Level
import globals
import glb


class Game:
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

    TILE_SIZE = 16

    def __init__(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if globals.play_sounds:
            pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.init()

        pygame.display.set_caption("Battle City")

        size = 480, 416

        if "-f" in sys.argv[1:]:
            globals.screen = pygame.display.set_mode(size, pygame.FULLglobals.screen)
        else:
            globals.screen = pygame.display.set_mode(size)

        self.clock = pygame.time.Clock()

        pygame.display.set_icon(globals.sprites.subsurface(0, 0, 13 * 2, 13 * 2))

        if globals.play_sounds:
            pygame.mixer.init(44100, -16, 1, 512)

            globals.sounds["start"] = pygame.mixer.Sound("sounds/gamestart.ogg")
            globals.sounds["end"] = pygame.mixer.Sound("sounds/gameover.ogg")
            globals.sounds["score"] = pygame.mixer.Sound("sounds/score.ogg")
            globals.sounds["bg"] = pygame.mixer.Sound("sounds/background.ogg")
            globals.sounds["fire"] = pygame.mixer.Sound("sounds/fire.ogg")
            globals.sounds["bonus"] = pygame.mixer.Sound("sounds/bonus.ogg")
            globals.sounds["explosion"] = pygame.mixer.Sound("sounds/explosion.ogg")
            globals.sounds["brick"] = pygame.mixer.Sound("sounds/brick.ogg")
            globals.sounds["steel"] = pygame.mixer.Sound("sounds/steel.ogg")

        self.enemy_life_image = globals.sprites.subsurface(81 * 2, 57 * 2, 7 * 2, 7 * 2)
        self.player_life_image = globals.sprites.subsurface(89 * 2, 56 * 2, 7 * 2, 8 * 2)
        self.flag_image = globals.sprites.subsurface(64 * 2, 49 * 2, 16 * 2, 15 * 2)

        self.player_image = pygame.transform.rotate(globals.sprites.subsurface(0, 0, 13 * 2, 13 * 2), 270)

        self.timefreeze = False

        self.font = pygame.font.Font("fonts/prstart.ttf", 16)

        self.im_game_over = pygame.Surface((64, 40))
        self.im_game_over.set_colorkey((0, 0, 0))
        self.im_game_over.blit(self.font.render("GAME", False, (127, 64, 64)), [0, 0])
        self.im_game_over.blit(self.font.render("OVER", False, (127, 64, 64)), [0, 20])
        self.game_over_y = 416 + 40

        self.nr_of_players = 1

        del globals.players[:]
        del globals.bullets[:]
        del globals.enemies[:]
        del globals.bonuses[:]

    def triggerBonus(self, bonus, player):
        if globals.play_sounds:
            globals.sounds["bonus"].play()

        player.trophies["bonus"] += 1
        player.score += 500

        if bonus.bonus == bonus.BONUS_GRENADE:
            for enemy in globals.enemies:
                enemy.explode()
        elif bonus.bonus == bonus.BONUS_HELMET:
            self.shieldPlayer(player, True, 10000)
        elif bonus.bonus == bonus.BONUS_SHOVEL:
            self.level.buildFortress(self.level.TILE_STEEL)
            gtimer.add(10000, lambda: self.level.buildFortress(self.level.TILE_BRICK), 1)
        elif bonus.bonus == bonus.BONUS_STAR:
            player.superpowers += 1
            if player.superpowers == 2:
                player.max_active_bullets = 2
        elif bonus.bonus == bonus.BONUS_TANK:
            player.lives += 1
        elif bonus.bonus == bonus.BONUS_TIMER:
            self.toggleEnemyFreeze(True)
            gtimer.add(10000, lambda: self.toggleEnemyFreeze(False), 1)
        globals.bonuses.remove(bonus)

        globals.labels.append(Label(bonus.rect.topleft, "500", 500))

    def shieldPlayer(self, player, shield=True, duration=None):
        player.shielded = shield
        if shield:
            player.timer_uuid_shield = gtimer.add(100, lambda: player.toggleShieldImage())
        else:
            gtimer.destroy(player.timer_uuid_shield)

        if shield and duration is not None:
            gtimer.add(duration, lambda: self.shieldPlayer(player, False), 1)

    def spawnEnemy(self):
        if len(globals.enemies) >= self.level.max_active_enemies:
            return
        if len(self.level.enemies_left) < 1 or self.timefreeze:
            return
        enemy = Enemy(self.level, 1)

        globals.enemies.append(enemy)

    def respawnPlayer(self, player, clear_scores=False):
        player.reset()

        if clear_scores:
            player.trophies = {
                "bonus": 0, "enemy0": 0, "enemy1": 0, "enemy2": 0, "enemy3": 0
            }

        self.shieldPlayer(player, True, 4000)

    def gameOver(self):
        print("Game Over")
        if globals.play_sounds:
            for sound in globals.sounds:
                globals.sounds[sound].stop()
            globals.sounds["end"].play()

        self.game_over_y = 416 + 40

        self.game_over = True
        gtimer.add(3000, lambda: self.showScores(), 1)

    def gameOverscreen(self):
        self.running = False

        globals.screen.fill([0, 0, 0])

        self.writeInBricks("game", [125, 140])
        self.writeInBricks("over", [125, 220])
        pygame.display.flip()

        while 1:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.showMenu()
                        return

    def showMenu(self):
        self.running = False

        del gtimer.timers[:]

        self.stage = 1

        self.animateIntroScreen()

        main_loop = True
        while main_loop:
            time_passed = self.clock.tick(50)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit()
                    elif event.key == pygame.K_UP:
                        if self.nr_of_players == 2:
                            self.nr_of_players = 1
                            self.drawIntroscreen()
                    elif event.key == pygame.K_DOWN:
                        if self.nr_of_players == 1:
                            self.nr_of_players = 2
                            self.drawIntroscreen()
                    elif event.key == pygame.K_RETURN:
                        main_loop = False

        del globals.players[:]
        self.nextLevel()

    def reloadplayers(self):
        if len(globals.players) == 0:
            x = 8 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
            y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2

            player = Player(
                self.level, 0, [x, y], self.DIR_UP, (0, 0, 13 * 2, 13 * 2)
            )
            globals.players.append(player)

            if self.nr_of_players == 2:
                x = 16 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                player = Player(
                    self.level, 0, [x, y], self.DIR_UP, (16 * 2, 0, 13 * 2, 13 * 2)
                )
                player.controls = [102, 119, 100, 115, 97]
                globals.players.append(player)

        for player in globals.players:
            player.level = self.level
            self.respawnPlayer(player, True)

    def showScores(self):
        self.running = False

        del gtimer.timers[:]

        if globals.play_sounds:
            for sound in globals.sounds:
                globals.sounds[sound].stop()

        if self.game_over:
            self.gameOverscreen()
        else:
            self.nextLevel()

    def draw(self):
        globals.screen.fill([0, 0, 0])

        self.level.draw([self.level.TILE_EMPTY, self.level.TILE_BRICK, self.level.TILE_STEEL, self.level.TILE_FROZE,
                         self.level.TILE_WATER])

        glb.castle.draw()

        for enemy in globals.enemies:
            enemy.draw()

        for label in globals.labels:
            label.draw()

        for player in globals.players:
            player.draw()

        for bullet in globals.bullets:
            bullet.draw()

        for bonus in globals.bonuses:
            bonus.draw()

        self.level.draw([self.level.TILE_GRASS])

        if self.game_over:
            if self.game_over_y > 188:
                self.game_over_y -= 4
            globals.screen.blit(self.im_game_over, [176, self.game_over_y])

        self.drawSidebar()

        pygame.display.flip()

    def drawSidebar(self):
        x = 416
        y = 0
        globals.screen.fill([100, 100, 100], pygame.Rect([416, 0], [64, 416]))

        xpos = x + 16
        ypos = y + 16

        for n in range(len(self.level.enemies_left) + len(globals.enemies)):
            globals.screen.blit(self.enemy_life_image, [xpos, ypos])
            if n % 2 == 1:
                xpos = x + 16
                ypos += 17
            else:
                xpos += 17

        if pygame.font.get_init():
            text_color = pygame.Color('black')
            for n in range(len(globals.players)):
                if n == 0:
                    globals.screen.blit(self.font.render(str(n + 1) + "P", False, text_color), [x + 16, y + 200])
                    globals.screen.blit(self.font.render(str(globals.players[n].lives), False, text_color),
                                        [x + 31, y + 215])
                    globals.screen.blit(self.player_life_image, [x + 17, y + 215])
                else:
                    globals.screen.blit(self.font.render(str(n + 1) + "P", False, text_color), [x + 16, y + 240])
                    globals.screen.blit(self.font.render(str(globals.players[n].lives), False, text_color),
                                        [x + 31, y + 255])
                    globals.screen.blit(self.player_life_image, [x + 17, y + 255])

            globals.screen.blit(self.flag_image, [x + 17, y + 280])
            globals.screen.blit(self.font.render(str(self.stage), False, text_color), [x + 17, y + 312])

    def drawIntroscreen(self, put_on_surface=True):
        globals.screen.fill([0, 0, 0])

        if pygame.font.get_init():


            globals.screen.blit(self.font.render("1 PLAYER", True, pygame.Color('white')), [165, 250])
            globals.screen.blit(self.font.render("2 PLAYER", True, pygame.Color('white')), [165, 275])


        if self.nr_of_players == 1:
            globals.screen.blit(self.player_image, [125, 245])
        elif self.nr_of_players == 2:
            globals.screen.blit(self.player_image, [125, 270])

        self.writeInBricks("battle", [65, 80])
        self.writeInBricks("city", [129, 160])

        if put_on_surface:
            pygame.display.flip()

    def animateIntroScreen(self):
        self.drawIntroscreen(False)
        screen_cp = globals.screen.copy()

        globals.screen.fill([0, 0, 0])

        y = 416
        while y > 0:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        y = 0
                        break

            globals.screen.blit(screen_cp, [0, y])
            pygame.display.flip()
            y -= 5

        globals.screen.blit(screen_cp, [0, 0])
        pygame.display.flip()

    def chunks(self, l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]

    def writeInBricks(self, text, pos):
        bricks = globals.sprites.subsurface(56 * 2, 64 * 2, 8 * 2, 8 * 2)
        brick1 = bricks.subsurface((0, 0, 8, 8))
        brick2 = bricks.subsurface((8, 0, 8, 8))
        brick3 = bricks.subsurface((8, 8, 8, 8))
        brick4 = bricks.subsurface((0, 8, 8, 8))

        alphabet = {
            "a": "0071b63c7ff1e3",
            "b": "01fb1e3fd8f1fe",
            "c": "00799e0c18199e",
            "e": "01fb060f98307e",
            "g": "007d860cf8d99f",
            "i": "01f8c183060c7e",
            "l": "0183060c18307e",
            "m": "018fbffffaf1e3",
            "o": "00fb1e3c78f1be",
            "r": "01fb1e3cff3767",
            "t": "01f8c183060c18",
            "v": "018f1e3eef8e08",
            "y": "019b3667860c18"
        }

        abs_x, abs_y = pos

        for letter in text.lower():

            binstr = ""
            for h in self.chunks(alphabet[letter], 2):
                binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
            binstr = binstr[7:]

            x, y = 0, 0
            letter_w = 0
            surf_letter = pygame.Surface((56, 56))
            for j, row in enumerate(self.chunks(binstr, 7)):
                for i, bit in enumerate(row):
                    if bit == "1":
                        if i % 2 == 0 and j % 2 == 0:
                            surf_letter.blit(brick1, [x, y])
                        elif i % 2 == 1 and j % 2 == 0:
                            surf_letter.blit(brick2, [x, y])
                        elif i % 2 == 1 and j % 2 == 1:
                            surf_letter.blit(brick3, [x, y])
                        elif i % 2 == 0 and j % 2 == 1:
                            surf_letter.blit(brick4, [x, y])
                        if x > letter_w:
                            letter_w = x
                    x += 8
                x = 0
                y += 8
            globals.screen.blit(surf_letter, [abs_x, abs_y])
            abs_x += letter_w + 16

    def toggleEnemyFreeze(self, freeze=True):
        for enemy in globals.enemies:
            enemy.paused = freeze
        self.timefreeze = freeze


    def finishLevel(self):
        if globals.play_sounds:
            globals.sounds["bg"].stop()

        self.active = False
        gtimer.add(3000, lambda: self.showScores(), 1)

        print("Stage " + str(self.stage) + " completed")

    def nextLevel(self):
        del globals.bullets[:]
        del globals.enemies[:]
        del globals.bonuses[:]
        glb.castle.rebuild()
        del gtimer.timers[:]

        self.stage += 1
        self.level = Level(self.stage)
        self.timefreeze = False

        levels_enemies = (
            (18, 2, 0, 0), (14, 4, 0, 2), (14, 4, 0, 2), (2, 5, 10, 3), (8, 5, 5, 2),
            (9, 2, 7, 2), (7, 4, 6, 3), (7, 4, 7, 2), (6, 4, 7, 3), (12, 2, 4, 2),
            (5, 5, 4, 6), (0, 6, 8, 6), (0, 8, 8, 4), (0, 4, 10, 6), (0, 2, 10, 8),
            (16, 2, 0, 2), (8, 2, 8, 2), (2, 8, 6, 4), (4, 4, 4, 8), (2, 8, 2, 8),
            (6, 2, 8, 4), (6, 8, 2, 4), (0, 10, 4, 6), (10, 4, 4, 2), (0, 8, 2, 10),
            (4, 6, 4, 6), (2, 8, 2, 8), (15, 2, 2, 1), (0, 4, 10, 6), (4, 8, 4, 4),
            (3, 8, 3, 6), (6, 4, 2, 8), (4, 4, 4, 8), (0, 10, 4, 6), (0, 6, 4, 10)
        )

        if self.stage <= 35:
            enemies_l = levels_enemies[self.stage - 1]
        else:
            enemies_l = levels_enemies[34]

        self.level.enemies_left = [0] * enemies_l[0] + [1] * enemies_l[1] + [2] * enemies_l[2] + [3] * enemies_l[3]
        random.shuffle(self.level.enemies_left)

        if globals.play_sounds:
            globals.sounds["start"].play()
            gtimer.add(4330, lambda: globals.sounds["bg"].play(-1), 1)

        self.reloadplayers()

        gtimer.add(3000, lambda: self.spawnEnemy())

        self.game_over = False

        self.running = True

        self.active = True

        self.draw()

        while self.running:

            time_passed = self.clock.tick(50)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                elif event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN and not self.game_over and self.active:

                    if event.key == pygame.K_q:
                        quit()
                    elif event.key == pygame.K_m:
                        globals.play_sounds = not globals.play_sounds
                        if not globals.play_sounds:
                            pygame.mixer.stop()
                        else:
                            globals.sounds["bg"].play(-1)

                    for player in globals.players:
                        if player.state == player.STATE_ALIVE:
                            try:
                                index = player.controls.index(event.key)
                            except:
                                pass
                            else:
                                if index == 0:
                                    if player.fire() and globals.play_sounds:
                                        globals.sounds["fire"].play()
                                elif index == 1:
                                    player.pressed[0] = True
                                elif index == 2:
                                    player.pressed[1] = True
                                elif index == 3:
                                    player.pressed[2] = True
                                elif index == 4:
                                    player.pressed[3] = True
                elif event.type == pygame.KEYUP and not self.game_over and self.active:
                    for player in globals.players:
                        if player.state == player.STATE_ALIVE:
                            try:
                                index = player.controls.index(event.key)
                            except:
                                pass
                            else:
                                if index == 1:
                                    player.pressed[0] = False
                                elif index == 2:
                                    player.pressed[1] = False
                                elif index == 3:
                                    player.pressed[2] = False
                                elif index == 4:
                                    player.pressed[3] = False

            for player in globals.players:
                if player.state == player.STATE_ALIVE and not self.game_over and self.active:
                    if player.pressed[0]:
                        player.move(self.DIR_UP)
                    elif player.pressed[1]:
                        player.move(self.DIR_RIGHT)
                    elif player.pressed[2]:
                        player.move(self.DIR_DOWN)
                    elif player.pressed[3]:
                        player.move(self.DIR_LEFT)
                player.update(time_passed)

            for enemy in globals.enemies:
                if enemy.state == enemy.STATE_DEAD and not self.game_over and self.active:
                    globals.enemies.remove(enemy)
                    if len(self.level.enemies_left) == 0 and len(globals.enemies) == 0:
                        self.finishLevel()
                else:
                    enemy.update(time_passed)

            if not self.game_over and self.active:
                for player in globals.players:
                    if player.state == player.STATE_ALIVE:
                        if player.bonus is not None and player.side == player.SIDE_PLAYER:
                            self.triggerBonus(bonus, player)
                            player.bonus = None
                    elif player.state == player.STATE_DEAD:
                        self.superpowers = 0
                        player.lives -= 1
                        if player.lives > 0:
                            self.respawnPlayer(player)
                        else:
                            self.gameOver()

            for bullet in globals.bullets:
                if bullet.state == bullet.STATE_REMOVED:
                    globals.bullets.remove(bullet)
                else:
                    bullet.update()

            for bonus in globals.bonuses:
                if not bonus.active:
                    globals.bonuses.remove(bonus)

            for label in globals.labels:
                if not label.active:
                    globals.labels.remove(label)

            if not self.game_over:
                if not glb.castle.active:
                    self.gameOver()

            gtimer.update(time_passed)

            self.draw()
