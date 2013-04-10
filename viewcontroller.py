#-*-coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Battleship View and Controller
# Purpose:     viewcontroller part for battleship game
#
# Author:      SG
# Copyright:   (c) SG 2013
#-------------------------------------------------------------------------------
#

import itertools

import pygame
import pygame.locals as loc

import model


CELL_SIZE = 20
size = 10


class Cell(pygame.sprite.Sprite):
    def __init__(self, image, coord, position):
        pygame.sprite.Sprite.__init__(self)
        self.i = coord[0]
        self.j = coord[1]
        self.position = position
        self.image = image
        self.draw()

    def draw(self):
        screen = pygame.display.get_surface()
        im = pygame.image.load('images/' + self.image + '.png')
        if self.position == 'left':
            screen.blit(im, (20 + self.i * CELL_SIZE, 20 + self.j * CELL_SIZE))
        else:
            screen.blit(im,
                        (300 + self.i * CELL_SIZE, 20 + self.j * CELL_SIZE))


class Ship(pygame.sprite.Sprite):
    def __init__(self, length, coord):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(coord, (length * CELL_SIZE, CELL_SIZE))
        self.image = Images.ship(length)
        self.length = length
        self.coord = coord
        self.position = 'horisontal'
        self.width = length * CELL_SIZE
        self.height = CELL_SIZE
        self.offset = None
        self.cells = None

    def draw(self):
        screen = pygame.display.get_surface()
        screen.blit(self.image, (self.coord[0], self.coord[1]))

    def turn_another_way(self):
        self.width, self.height = self.height, self.width
        self.rect = pygame.Rect(self.coord,
                                (self.width, self.height))

        if self.position == 'vertical':
            self.position = 'horisontal'
        else:
            self.position = 'vertical'
        self.image = pygame.transform.rotate(self.image, 90)

    def does_not_cross(self, other):
        def proper_distance(point1, point2):
            dist = (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
            return dist > 2

        assert self.cells
        assert other.cells
        return all(proper_distance(i, j)
                   for i in self.cells for j in other.cells)


class Board(object):
    def __init__(self, board, position):
        self.board = board
        self.position = position

    def draw(self):
        for i in xrange(size):
            for j in xrange(size):
                Cell(self.board[i][j], (i, j), self.position)


class AcceptButton(pygame.sprite.Sprite):
    def __init__(self, coord): #coord is tuple
        pygame.sprite.Sprite.__init__(self)
        self.coord = coord
        self.rect = pygame.Rect(self.coord, (200, 100))
        self.image = pygame.image.load('images/unable_button.png')
        self.marker = 'unable'

    def draw(self):
        screen = pygame.display.get_surface()
        screen.blit(self.image, self.coord)

    def make_button_able(self):
        self.marker = 'able'
        self.image = Images.able_button

    def make_button_unable(self):
        self.marker = 'unable'
        self.image = Images.unable_button


class WinMessage(pygame.sprite.Sprite):
    def __init__(self, winner):
        pygame.sprite.Sprite.__init__(self)
        self.coord = (120, 250)
        self.winner = winner

    def draw(self):
        screen = pygame.display.get_surface()
        if self.winner == 'computer':
            self.image = Images.computer_won
        else:
            self.image = Images.you_won
        screen.blit(self.image, self.coord)


class Images(object):
    icon = pygame.image.load('images/icon.png')
    computer_won = pygame.image.load('images/computerwon.png')
    you_won = pygame.image.load('images/youwon.png')
    empty_field = pygame.image.load('images/empty_field.png')
    able_button = pygame.image.load('images/able_button.png')
    unable_button = pygame.image.load('images/unable_button.png')

    @classmethod
    def ship(cls, length):
        return pygame.image.load('images/sh%d.png' % length)


class Game(object):
    screen_dimensions = (600, 600)
    button_dimensions = (20, 45)

    # Game states
    user_sets_ships = 1
    user_turn = 2
    computer_turn = 3
    end_game = 4

    # Events
    ships_are_ready_milord = pygame.USEREVENT + 1
    ship_was_moved_milord = ships_are_ready_milord + 1
    turn_is_made = ship_was_moved_milord + 1
    user_hit = turn_is_made + 1
    user_miss = user_hit + 1
    computer_hit = user_miss + 1
    computer_miss = computer_hit + 1

    def __init__(self):
        pygame.init()
        pygame.display.set_mode(Game.screen_dimensions)
        pygame.display.set_caption('Battleship')
        pygame.display.set_icon(Images.icon.convert())

        self.button = AcceptButton(Game.button_dimensions)

        self.ships = self.ships_for_milord()

        self.drawable = []
        self.drawable.extend(self.ships)
        self.drawable.append(self.button)

        self.state = Game.user_sets_ships

        self.updated = True
        self.loop()

    def loop(self):
        while True:
            event = pygame.event.wait()
            self.handle_event(event)
            self.draw_all()

    def draw_all(self):
        if self.updated:
            screen = pygame.display.get_surface()
            screen.fill((255, 255, 255))
            screen.blit(Images.empty_field, (300, 20))
            for d in self.drawable:
                d.draw()

            pygame.display.flip()

    def handle_event(self, event):
        self.updated = True
        if event.type == pygame.QUIT:
            exit(0)

        elif self.state == Game.user_sets_ships:
            if event.type == loc.MOUSEBUTTONDOWN and event.button != 1:
                self.handle_right_click(event.pos)
            elif event.type == loc.MOUSEBUTTONDOWN:
                self.handle_other_click(event.pos)
            elif event.type == loc.MOUSEMOTION:
                self.handle_motion()
            elif event.type == loc.MOUSEBUTTONUP:
                self.stop_draggin()
            elif event.type == Game.ship_was_moved_milord:
                self.check_ships()
            elif event.type == Game.ships_are_ready_milord:
                self.prepare_computer_board()
                self.state = Game.user_turn
                return
            else:
                self.updated = True

        elif self.state == Game.user_turn:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x = (event.pos[0] - 20) // CELL_SIZE
                y = (event.pos[1] - 20) // CELL_SIZE
                self.do_user_turn(x, y)
            elif event.type == Game.user_hit:
                if self.enemy_field.check_end():
                    self.drawable.append(WinMessage('human'))
                    self.state = Game.end_game
                else:
                    self.state = Game.user_turn
            elif event.type == Game.user_miss:
                self.state = Game.computer_turn
                self.do_computer_turn()
            else:
                self.updated = True

        elif self.state == Game.computer_turn:
            if event.type == Game.computer_hit:
                if self.human.check_end():
                    self.drawable.append(WinMessage('computer'))
                    self.state = Game.end_game
                else:
                    self.state = Game.computer_turn
                    self.do_computer_turn()
            elif event.type == Game.computer_miss:
                self.state = Game.user_turn
            else:
                self.updated = True

    def handle_right_click(self, pos):
        for ship in self.ships:
            if ship.rect.collidepoint(pos):
                ship.turn_another_way()
                pygame.event.post(
                    pygame.event.Event(Game.ship_was_moved_milord))

    def handle_other_click(self, pos):
        if self.button.marker == 'able' and self.button.rect.collidepoint(pos):
            pygame.event.post(pygame.event.Event(Game.ships_are_ready_milord))
            return

        for ship in self.ships:
            if ship.rect.collidepoint(pos):
                mouse_x, mouse_y = pos
                my_x, my_y = ship.rect.topleft
                ship.offset = mouse_x - my_x, mouse_y - my_y

    def handle_motion(self):
        if not any(pygame.mouse.get_pressed()):
            return

        for ship in [ship for ship in self.ships if ship.offset]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            off_x, off_y = ship.offset
            x, y = mouse_x - off_x, mouse_y - off_y
            new_x = (x - 300) // CELL_SIZE
            new_y = (y - 20) // CELL_SIZE
            if new_x in range(size) and new_y in range(size):
                x = 300 + CELL_SIZE * new_x
                y = 20 + CELL_SIZE * new_y
                if ship.position == 'horisontal':
                    if new_x + ship.length <= size:
                        ship.cells = [(new_x + m, new_y) for m in
                                      xrange(ship.length)]
                else:
                    if new_y + ship.length <= size:
                        ship.cells = [(new_x, new_y + m) for m
                                      in xrange(ship.length)]
                pygame.event.post(
                    pygame.event.Event(Game.ship_was_moved_milord))
            else:
                ship.cells = None

            ship.rect.topleft = x, y
            ship.coord = ship.rect.topleft
            ship.rect = pygame.Rect(ship.rect.topleft,
                                    (ship.width, ship.height))

    def stop_draggin(self):
        for ship in self.ships:
            ship.offset = None

    def do_user_turn(self, x, y):
        a = self.user_move(x, y)
        if a == 'dot':
            pygame.event.post(pygame.event.Event(Game.user_miss))
        else:
            pygame.event.post(pygame.event.Event(Game.user_hit))

    def do_computer_turn(self):
        b = self.computer_move()
        if b == 'dot':
            pygame.event.post(pygame.event.Event(Game.computer_miss))
        else:
            pygame.event.post(pygame.event.Event(Game.computer_hit))

    def prepare_computer_board(self):
        self.drawable.remove(self.button)
        for ship in self.ships:
            self.drawable.remove(ship)

        self.human = model.Field(10, 'human')
        self.human.human_set_ships({ship: ship.cells for ship in self.ships})

        self.human_board = Board(self.human.board, 'right')
        self.drawable.append(self.human_board)

        self.computer_setting_ships()

        self.computer_board = Board(self.enemy_field.enemy_view, 'left')
        self.drawable.append(self.computer_board)

        self.refresh_fields()

    def check_possible_ships(self):
        all_s = [ship for ship in self.ships if ship.cells]
        if len(all_s) != 10:
            return False
        else:
            return all(a.does_not_cross(b) for a, b in
                       itertools.combinations(all_s, r=2))

    def check_ships(self):
        if self.check_possible_ships():
            self.button.make_button_able()
        else:
            self.button.make_button_unable()

    def user_move(self, x, y):
        if x in range(size) and y in range(size):
            if self.enemy_view[x][y] == 'empty':
                return self.shot_cycle((x, y), 'left')

    def computer_move(self):
        a = model.make_shot_computer(self.human)
        return a

    def computer_setting_ships(self):
        self.enemy_field = model.Field(10, 'computer')
        try:
            self.enemy_field.set_ships()
        except IndexError:
            self.computer_setting_ships()

    def refresh_fields(self):
        self.enemy_view = self.enemy_field.enemy_view
        self.enemy_board = self.enemy_field.board

    def shot_cycle(self, move, board_position):
        result = self.enemy_field.get_shot(move)
        self.enemy_field.refresh_ships()
        self.refresh_fields()
        return result

    def ships_for_milord(self):
        x, y = 300, 250
        return [Ship(1, (x, y)),
                Ship(1, (x + 30, y)),
                Ship(1, (x + 60, y)),
                Ship(1, (x + 90, y)),
                Ship(2, (x, y + 30)),
                Ship(2, (x + 50, y + 30)),
                Ship(2, (x + 100, y + 30)),
                Ship(3, (x, y + 60)),
                Ship(3, (x + 70, y + 60)),
                Ship(4, (x, y + 90)),
        ]


if __name__ == "__main__":
    Game()