# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Battleship Model
# Purpose:     functional part for battleship game
#
# Author:      SG
# Copyright:   (c) SG 2013
#-------------------------------------------------------------------------------
#
#

import random

empty = 'empty'

ship = 'ship'
dot = 'dot'

hit = 'hit'
miss = 'dot'


ships = { 'boat1': 1,
          'boat2': 1,
          'boat3': 1,
          'boat4': 1,

          'tallship1': 2,
          'tallship2': 2,
          'tallship3': 2,

          'submarine1': 3,
          'submarine2': 3,

          'destroyer': 4,
          }

position = ['ver', 'hor']
opposite = {'ver':'hor', 'hor':'ver'}

orientation = ['back', 'forward']
opposite_or = {'back':'forward', 'forward':'back'}

def inside(move, ship):
    return (move[0] >= ship[0][0] and move[0] <= ship[1][0] and move[1] >= ship[0][1] and move[1] <= ship[1][1])

def dots(array):
    final = []
    for dot in array:
        around = [(dot[0]-1, dot[1]-1),
                      (dot[0]-1, dot[1]),
                      (dot[0]-1, dot[1]+1),
                      (dot[0]+1, dot[1]-1),
                      (dot[0]+1, dot[1]),
                      (dot[0]+1, dot[1]+1),
                      (dot[0], dot[1]-1),
                      (dot[0], dot[1]+1),
                    ]
        for i in around:
            if i not in final:
                final.append(i)
    for dot in array:
        if dot in final:
            final.remove(dot)
    return final

class Field:
    def __init__(self, size, player): # player is 'computer' or 'human'
        self.board = [[empty]*size for i in range(size)]
        self.player = player
        self.size = size
        self.enemy_view = [[empty]*size for i in range(size)]
        self.last_move = None
        self.ships = []

    def __str__(self):
        return '\n'.join(''.join(i) for i in self.board) + '\n'

    def print_for_enemy(self):
        print '\n'.join(''.join(i) for i in self.enemy_view) + '\n'

    def get_possible_places(self, length, direction): # direction is 'hor' or 'ver'
        items = filter(lambda (x, y) : self.board[x][y] == empty, [(i,j) for i in xrange(self.size) for j in xrange(self.size)])
        final = []
        for (i,j) in items:
            if direction == 'hor':
                mark = 0
                for k in xrange(1,length):
                    if (i+k, j) in items:
                        mark += 1
                if mark == length-1:
                    final.append((i,j))
            else:
                mark = 0
                for k in xrange(1,length):
                    if (i, j+k) in items:
                        mark += 1
                if mark == length-1:
                    final.append((i,j))
        return final

    def set_ships(self):
        if self.player == 'computer':
            for i in ships: # random order because of dictionary
                pos = random.choice(position)
                start = random.choice(self.get_possible_places(ships[i],pos))
                ar = []
                if pos == 'hor':
                    for j in xrange(ships[i]):
                        self.board[start[0]+j][start[1]] = ship
                        ar.append((start[0]+j,start[1]))
                        if j == ships[i]-1:
                            self.ships.append([start, (start[0] + j, start[1]), 'alive'])
                else:
                    for j in xrange(ships[i]):
                        self.board[start[0]][start[1]+j] = ship
                        ar.append((start[0],start[1]+j))
                        if j == ships[i]-1:
                            self.ships.append([start, (start[0], start[1] + j), 'alive'])
                dots_ar = dots(ar)
                for m in dots_ar:
                    if m[0] in range(self.size) and m[1] in range(self.size) and self.board[m[0]][m[1]] == empty:
                        self.board[m[0]][m[1]] = dot

    def check_deadful_move(self, move):
        for j in self.ships:
            if inside(move,j):
                if self.check_ship(j):
                    return "ranen"
                else:
                    j[2] = 'dead'
                    return "ubit"


    def count_ships(self):
        self.refresh_ships()
        return len(filter(lambda (a,b,c) : c == 'alive', self.ships))

    def check_end(self):
        return self.count_ships() == 0

    def check_ship(self, this_ship):
        not_hit = 0
        for i in xrange(this_ship[0][0], this_ship[1][0]+1):
            for j in xrange(this_ship[0][1], this_ship[1][1]+1):
                if self.board[i][j] == ship:
                    not_hit += 1
        return not not_hit == 0

    def refresh_ships(self):
        for i in xrange(len(self.ships)):
            if not self.check_ship(self.ships[i]):
                self.ships[i][2] = 'dead'
                extra = [(e,f) for e in range(self.ships[i][0][0], self.ships[i][1][0]+1) for f in range(self.ships[i][0][1], self.ships[i][1][1]+1)]
                all_d = dots(extra)
                for (a,b) in all_d:
                    if a in range(self.size) and b in range(self.size):
                        self.enemy_view[a][b] = dot
                        self.board[a][b] = dot

    def get_shot(self, shot):
        if self.board[shot[0]][shot[1]] == ship:
            self.board[shot[0]][shot[1]] = hit
            self.enemy_view[shot[0]][shot[1]] = hit
            return hit
        else:
            self.board[shot[0]][shot[1]] = miss
            self.enemy_view[shot[0]][shot[1]] = dot
            return dot

    def pos_moves(self, item):
        final = {'ver': {}, 'hor': {}}
        if item[0] >= 1 and self.enemy_view[item[0]-1][item[1]] == empty:
            final['hor']['back'] = (item[0]-1, item[1])
        if item[0] <= self.size-2 and self.enemy_view[item[0]+1][item[1]] == empty:
            final['hor']['forward'] = (item[0]+1, item[1])
        if item[1] >= 1 and self.enemy_view[item[0]][item[1]-1] == empty:
            final['ver']['back'] = (item[0], item[1]-1)
        if item[1] <= self.size-2 and self.enemy_view[item[0]][item[1]+1] == empty:
            final['ver']['forward'] = (item[0], item[1]+1)
        return final

    def empties_for_enemy(self):
        return filter(lambda (i,j): self.enemy_view[i][j] == empty, [(x,y) for x in xrange(self.size) for y in xrange(self.size)])

    def next_step(self, item, vh, bf): #return next step to way
        i = 0
        if vh == 'ver':
            j = 0
            if bf == 'forward':
                i = 1
            else:
                i = -1
        else:
            i = 0
            if bf == 'forward':
                j = 1
            else:
                j = -1
        if item[0]+i in range(self.size) and item[1]+j in range(self.size):
            return (item[0]+i,item[1]+j)
        else:
            return None
    def human_set_ships(self, shipsset): #dictionary { ship obj: [(cell1, cell2), ...] }
        self.ships = [[square[0], square[-1], 'alive'] for _, square in shipsset.iteritems()]
        if self.player == 'human':
            for sh in self.ships:
                for i in xrange(sh[0][0], sh[1][0] + 1):
                    for j in xrange(sh[0][1], sh[1][1] + 1):
                        self.board[i][j] = ship


stack = []
start_move = (99,99)
next_move = (99,99)
a = ('', '')

def status_kvo():
    global stack, start_move, next_move, a
    stack = []
    start_move = (99,99)
    next_move = (99,99)
    a = ('', '')

def create_stack(field, move):
    way1 = random.choice(position)
    way2 = opposite[way1]
    orient1 = random.choice(orientation)
    orient2 = opposite_or[orient1]
    stack_whole = [(way1, orient1), (way1, orient2), (way2, orient1), (way2, orient2)]
    stack_final = []
    for i in xrange(4):
        ne = field.next_step(move, stack_whole[i][0], stack_whole[i][1])
        if ne and field.enemy_view[ne[0]][ne[1]] != 'dot':
            stack_final.append(stack_whole[i])
    return stack_final

def make_shot_computer(field): #user_field -> return result (hit or dot)
    global stack, start_move, next_move, a
    if a == ('', ''):
        start_move = random.choice(field.empties_for_enemy())
        stack = create_stack(field, start_move)
        if stack:
            a = stack.pop(0)
            next_move = field.next_step(start_move, a[0], a[1])
        if field.get_shot(start_move) == hit:
            if field.check_deadful_move(start_move) == 'ubit':
                status_kvo()
                field.refresh_ships()
            return 'hit'
        else:
            status_kvo()
            return 'dot'
    else:
        if field.get_shot(next_move) == hit:
            if field.check_deadful_move(next_move) == 'ubit':
                status_kvo()
                field.refresh_ships()
            else:
                next_move = field.next_step(next_move, a[0], a[1])
            return 'hit'
        else:
            a = stack.pop(0)
            next_move = field.next_step(start_move, a[0], a[1])
            return 'dot'