#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
import time

WIDTH=7
HEIGHT=7
HOMEX=3
HOMEY=3
FOODS=7
NBANTS=5

NOSTYLE, BOLD, UNDERLINE, INVERSE = range(4)
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
DEFAULT_COLOR = 9

class GameScreen(object):

    def __init__(self, game):
        self.game = game

    def clear(self):
        os.system("clear")

    def stylecode(self, style):
        default = "\033[0m"
        return {
            NOSTYLE: default,
            BOLD: "\033[1m",
            UNDERLINE: "\033[2m",
            INVERSE: "\033[3m",
            }.get(style, default)

    def fgcolorcode(self, color):
        return "\033[3%dm" % (color,)

    def bgcolorcode(self, color):
        return "\033[4%dm" % (color,)

    def fullstylecode(self, bgcolor, fgcolor, style):
        return self.stylecode(NOSTYLE) + \
               self.stylecode(style) + \
               self.bgcolorcode(bgcolor) + \
               self.fgcolorcode(fgcolor)

    def moveTo(self, x, y):
        sys.stdout.write("\033[%d;%dH" % (y,x))

    def writeAt(self, x, y, char, bgcolor, fgcolor, style):
        self.moveTo(x,y)
        sys.stdout.write(self.fullstylecode(bgcolor, fgcolor, style))
        sys.stdout.write(char)
        sys.stdout.write(self.stylecode(NOSTYLE))
        sys.stdout.flush()

    def drawVLine(self, x, sy, ey, bgcolor, fgcolor, style):
        y = sy
        while y < ey:
            self.writeAt(x, y, '|', bgcolor, fgcolor, style)
            y += 1

    def drawHLine(self, y, sx, ex, bgcolor, fgcolor, style):
        x = sx
        while x < ex:
            self.writeAt(x, y, '-', bgcolor, fgcolor, style)
            x += 1

    def drawMap(self):
        for x in range(WIDTH):
            self.writeAt((4*x)+6,2,str(x+1),DEFAULT_COLOR,RED,BOLD)
            self.drawVLine((4*x)+4, 1, HEIGHT*4+4, DEFAULT_COLOR, RED, BOLD)
        self.drawVLine((4*(x+1))+4, 1, HEIGHT*4+4, DEFAULT_COLOR, RED, BOLD)
        for y in range(HEIGHT):
            self.writeAt(2,(4*y)+6,str(y+1),DEFAULT_COLOR,RED,BOLD)
            self.drawHLine((4*y)+4, 1, WIDTH*4+4, DEFAULT_COLOR, RED, BOLD)
        self.drawHLine((4*(y+1))+4, 1, WIDTH*4+4, DEFAULT_COLOR, RED, BOLD)

        def map2screen(xm, ym):
            return ((xm*4) + 6, (ym*4) + 6)

        amap = self.game.map

        for x in range(WIDTH):
            for y in range(HEIGHT):
                xs, ys = map2screen(x, y)
                mc = amap.cell(x, y)
                ph = amap.pheromones[y][x]
                fo = amap.food[y][x]
                self.writeAt(xs-1, ys-1, unicode(mc), DEFAULT_COLOR, GREEN, NOSTYLE)
                if ph > 0:
                    self.writeAt(xs-1, ys+1, unicode(ph), DEFAULT_COLOR, MAGENTA, NOSTYLE)
                if fo > 0:
                    self.writeAt(xs+1, ys-1, unicode(fo), DEFAULT_COLOR, GREEN, NOSTYLE)

        for a in self.game.ants:
            ax, ay = map2screen(a.x, a.y)
            self.writeAt(ax, ay, a.DIR_IMAGE.get(a.direction), DEFAULT_COLOR, YELLOW, BOLD)

        self.moveTo(1, HEIGHT * 4 + 7)

    def askQuestion(self, questions):
        answers = []
        for i, q in enumerate(questions):
            text, choices = q
            choices = [str(c) for c in choices]
            answer = None
            while answer not in choices:
                self.writeAt(WIDTH * 4 + 10, i*2 + 1,
                    u"%s (%s) : " % (text, choices), DEFAULT_COLOR, YELLOW, UNDERLINE)
                answer = raw_input()
            answers.append(answer)
        return answers

class Map(object):
    NORTH, EAST, SOUTH, WEST, TLEFT, TRIGHT = range(6)
    TILE_IMAGE = {
        TLEFT: u"↶",
        TRIGHT: u"↷",
        NORTH: u"⇡",
        EAST: u"⇢",
        SOUTH: u"⇣",
        WEST: u"⇠",
        }
    TURNCARDS = (TLEFT, TRIGHT)
    MOVECARDS = (TLEFT, TRIGHT, NORTH, EAST, WEST, SOUTH)
    HEADCARDS = (NORTH, EAST, SOUTH, WEST)
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.map = [[random.choice([self.TLEFT, self.TRIGHT]) for x in range(self.width)] for y in range(self.height)]
        self.pheromones = [[0 for x in range(self.width)] for y in range(self.height)]
        self.curstep = 0
        self.evaporation = 20
        self.food = [[0 for x in range(self.width)] for y in range(self.height)]
        for i in range(FOODS):
            self.food[random.randrange(self.height)][random.randrange(self.width)] += 5

        self.pheromones_deck=range(20)

    def add(self, x, y):
        if self.pheromones[y][x] == 0:
            self.pheromones[y][x] = self.pheromones_deck.pop()

    def getcell(self, x, y):
        return self.map[y][x]

    def switch(self, x, y):
        o = self.getcell(x,y)
        self.map[y][x] = {
            self.TLEFT: self.TRIGHT,
            self.TRIGHT: self.TLEFT,
            }.get(o, o)

    def cell(self, x, y):
        return self.TILE_IMAGE.get(self.map[y][x], u"?")

    def step(self):
        self.curstep += 1
        if self.curstep > self.evaporation:
            for y in range(self.height):
                for x in range(self.width):
                    if self.pheromones[y][x] > 0:
                        self.pheromones_deck.append(self.pheromones[y][x])
                        self.pheromones[y][x] = 0
            self.curstep = 0

class Ant(object):
    NORTH, EAST, SOUTH, WEST = range(4)
    DIR_IMAGE = {
        NORTH: u"⇡",
        EAST: u"⇢",
        SOUTH: u"⇣",
        WEST: u"⇠",
        }

    def __init__(self, map):
        self.x = HOMEX
        self.y = HOMEY
        self.map = map
        self.direction = random.choice([self.NORTH, self.EAST, self.SOUTH, self.WEST])
        self.foodfound = False

    def move(self, many):
        for i in range(many):
            self.moveone()

    def oldmoveone(self):
        if self.direction == self.NORTH and self.y > 0:
            self.y -= 1
        elif self.direction == self.SOUTH and self.y < HEIGHT-1:
            self.y += 1
        elif self.direction == self.EAST and self.x < WIDTH-1:
            self.x += 1
        elif self.direction == self.WEST and self.x > 0:
            self.x -= 1

    def moveone(self):
        if self.direction == self.NORTH:
            self.y -= 1
        elif self.direction == self.SOUTH:
            self.y += 1
        elif self.direction == self.EAST:
            self.x += 1
        elif self.direction == self.WEST:
            self.x -= 1

        if  self.y == HEIGHT or \
            self.y < 0 or \
            self.x == WIDTH or \
            self.x < 0:

            self.x = HOMEX
            self.y = HOMEY
            self.foodfound = False

    def rotate(self, rotation):
        if rotation == Map.TLEFT:
            self.direction -= 1
            if self.direction < self.NORTH:
                self.direction = self.WEST
        elif rotation == Map.TRIGHT:
            self.direction += 1
            if self.direction > self.WEST:
                self.direction = self.NORTH

    def headhome(self):
        if self.x == HOMEX and self.y == HOMEY:
            self.foodfound = False
        else:
            self.map.add(self.x, self.y)
            if self.x > HOMEX:
                self.direction = self.WEST
            elif self.y < HOMEY:
                self.direction = self.SOUTH
            elif self.x < HOMEX:
                self.direction = self.EAST
            elif self.y > HOMEY:
                self.direction = self.NORTH
            self.move(1)

    def find_bigger_pheromone(self):
        ax, ay = self.x, self.y
        neigh = [
            # (ax-1, ay-1),
            (ax-1, ay  ),
            # (ax-1, ay+1),
            (ax  , ay-1),
            (ax  , ay+1),
            # (ax+1, ay-1),
            (ax+1, ay  ),
            # (ax+1, ay+1),
            ]
        max_ph = [0,ax,ay]
        for x, y in neigh:
            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                continue
            ph = self.map.pheromones[y][x]
            if ph > max_ph[0]:
                max_ph = [ph, x, y]
        if max_ph[0] != 0:
            return max_ph[1:]

    def step(self):
        ax, ay= self.x, self.y
        if self.foodfound:
            self.headhome()
        else:
            card = self.map.getcell(ax,ay)
            bph = self.find_bigger_pheromone()
            if bph:
                bx, by = bph
                if self.x > bx:
                    self.direction = self.WEST
                if self.y < by:
                    self.direction = self.SOUTH
                if self.x < bx:
                    self.direction = self.EAST
                if self.y > by:
                    self.direction = self.NORTH
                self.move(1)
            else:
                if card in Map.TURNCARDS:
                    self.rotate(self.map.getcell(ax,ay))
                    self.map.switch(ax, ay)
                elif card in Map.HEADCARDS:
                    self.direction = card
                if card in Map.MOVECARDS:
                    self.move(1)
            ax, ay= self.x, self.y
            if self.map.food[ay][ax] > 0:
                self.map.food[ay][ax] -= 1
                self.foodfound = True

class Game(object):

    def __init__(self):
        self.map = Map()
        self.ants = [Ant(self.map) for i in range(NBANTS)]

    def step(self):
        self.map.step()
        for a in self.ants:
            a.step()

    def changeCard(self, new_card_data):
        x, y, n = new_card_data
        x = int(x) - 1
        y = int(y) - 1
        newcard = {
            'n':Map.NORTH,
            's':Map.SOUTH,
            'e':Map.EAST,
            'w':Map.WEST,
            }[n]
        self.map.map[y][x] = newcard

def main():
    g = Game()
    s = GameScreen(g)
    running = True
    while running:
        s.clear()
        s.drawMap()
        a = raw_input()
        if a == "q":
            running = False
        elif a == "c":
            g.changeCard(s.askQuestion([
                (u"x", range(1,WIDTH+1)),
                (u"y", range(1,HEIGHT+1)),
                (u"new", [u"n","s","e","w"],)
                ]))
        g.step()

if __name__ == "__main__":
    main()
