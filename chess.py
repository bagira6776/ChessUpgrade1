import pygame
from pygame.locals import *
import random

from piece import Piece
from utils import Utils

import time
pygame.mixer.init()
move_sounds = [
    pygame.mixer.Sound("sounds/move1.mp3"),
    pygame.mixer.Sound("sounds/move2.mp3"),
]


class Chess(object):
    def __init__(self, screen, pieces_src, square_coords, square_length):
        # поверхня відображення
        self.screen = screen
        # створити об'єкт класу для відображення шахових фігур на дошці
        self.chess_pieces = Piece(pieces_src, cols=6, rows=2)
        # зберегти координати клітинок шахівниці
        self.board_locations = square_coords
        # довжина сторони клітинки шахівниці
        self.square_length = square_length
        # словник для відстеження черговості ходу гравців
        self.turn = {"black": 0,
                     "white": 0}

        # список можливих ходів для вибраної фігури
        self.moves = []
        #
        self.utils = Utils()

        # відповідність назв фігур індексам у списку координат фігур на спрайт-листі
        self.pieces = {
            "white_pawn": 5,
            "white_knight": 3,
            "white_bishop": 2,
            "white_rook": 4,
            "white_king": 0,
            "white_queen": 1,
            "black_pawn": 11,
            "black_knight": 9,
            "black_bishop": 8,
            "black_rook": 10,
            "black_king": 6,
            "black_queen": 7
        }

        # список захоплених фігур
        self.captured = []
        #
        self.winner = ""

        # Словник для відстеження, чи робили король або тури ходи (потрібно для рокірування)
        self.has_moved = {
            "white_king": False,
            "white_rook_a": False,  # тура на лінії 'a' (довге рокірування)
            "white_rook_h": False,  # тура на лінії 'h' (коротке рокірування)
            "black_king": False,
            "black_rook_a": False,
            "black_rook_h": False
        }

        self.reset()

    def reset(self):
        # очистити список ходів
        self.moves = []

        # випадковим чином визначити черговість ходу гравця
        x = random.randint(0, 1)
        if (x == 1):
            self.turn["black"] = 1
        elif (x == 0):
            self.turn["white"] = 1

        # двовимірний словник, що містить деталі про кожну позицію на дошці
        # формат зберігання: [назва_фігури, чи_вибрана_зараз, координати_x_y]
        self.piece_location = {}
        x = 0
        for i in range(97, 105):
            a = 8
            y = 0
            self.piece_location[chr(i)] = {}
            while a > 0:
                # [назва фігури, чи вибрана зараз, координати на дошці]
                self.piece_location[chr(i)][a] = ["", False, [x, y]]
                a = a - 1
                y = y + 1
            x = x + 1

        # скинути стан дошки
        for i in range(97, 105):
            x = 8
            while x > 0:
                if (x == 8):
                    if (chr(i) == 'a' or chr(i) == 'h'):
                        self.piece_location[chr(i)][x][0] = "black_rook"
                    elif (chr(i) == 'b' or chr(i) == 'g'):
                        self.piece_location[chr(i)][x][0] = "black_knight"
                    elif (chr(i) == 'c' or chr(i) == 'f'):
                        self.piece_location[chr(i)][x][0] = "black_bishop"
                    elif (chr(i) == 'd'):
                        self.piece_location[chr(i)][x][0] = "black_queen"
                    elif (chr(i) == 'e'):
                        self.piece_location[chr(i)][x][0] = "black_king"
                elif (x == 7):
                    self.piece_location[chr(i)][x][0] = "black_pawn"
                elif (x == 2):
                    self.piece_location[chr(i)][x][0] = "white_pawn"
                elif (x == 1):
                    if (chr(i) == 'a' or chr(i) == 'h'):
                        self.piece_location[chr(i)][x][0] = "white_rook"
                    elif (chr(i) == 'b' or chr(i) == 'g'):
                        self.piece_location[chr(i)][x][0] = "white_knight"
                    elif (chr(i) == 'c' or chr(i) == 'f'):
                        self.piece_location[chr(i)][x][0] = "white_bishop"
                    elif (chr(i) == 'd'):
                        self.piece_location[chr(i)][x][0] = "white_queen"
                    elif (chr(i) == 'e'):
                        self.piece_location[chr(i)][x][0] = "white_king"
                x = x - 1

    def play_turn(self):
        # білий колір
        white_color = (255, 255, 255)
        # створити шрифти для тексту
        small_font = pygame.font.SysFont("comicsansms", 20)
        # створити текст, який буде відображатися в ігровому меню
        if self.turn["black"]:
            turn_text = small_font.render("Turn: Black", True, white_color)
        elif self.turn["white"]:
            turn_text = small_font.render("Turn: White", True, white_color)

        # показати привітальний текст / текст ходу
        self.screen.blit(turn_text,
                         ((self.screen.get_width() - turn_text.get_width()) // 2, 10))

        # дозволити грати гравцю з чорними фігурами
        if (self.turn["black"]):
            self.move_piece("black")
        # дозволити грати гравцю з білими фігурами
        elif (self.turn["white"]):
            self.move_piece("white")

    # метод для малювання фігур на шахівниці
    def draw_pieces(self):
        transparent_green = (0, 194, 39, 170)
        transparent_blue = (28, 21, 212, 170)

        # створити прозору поверхню
        surface = pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA)
        surface.fill(transparent_green)

        surface1 = pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA)
        surface1.fill(transparent_blue)

        # цикл для зміни фонового кольору вибраної фігури
        for val in self.piece_location.values():
            for value in val.values():
                # назва фігури в поточній позиції
                piece_name = value[0]
                # координати x, y поточної фігури
                piece_coord_x, piece_coord_y = value[2]

                # змінити колір фону фігури, якщо вона вибрана
                if value[1] and len(value[0]) > 5:
                    # якщо вибрана фігура — чорна
                    if value[0][:5] == "black":
                        self.screen.blit(surface, self.board_locations[piece_coord_x][piece_coord_y])
                        if len(self.moves) > 0:
                            for move in self.moves:
                                x_coord = move[0]
                                y_coord = move[1]
                                if x_coord >= 0 and y_coord >= 0 and x_coord < 8 and y_coord < 8:
                                    self.screen.blit(surface, self.board_locations[x_coord][y_coord])
                    # якщо вибрана фігура — біла
                    elif value[0][:5] == "white":
                        self.screen.blit(surface1, self.board_locations[piece_coord_x][piece_coord_y])
                        if len(self.moves) > 0:
                            for move in self.moves:
                                x_coord = move[0]
                                y_coord = move[1]
                                if x_coord >= 0 and y_coord >= 0 and x_coord < 8 and y_coord < 8:
                                    self.screen.blit(surface1, self.board_locations[x_coord][y_coord])

        # намалювати всі шахові фігури
        for val in self.piece_location.values():
            for value in val.values():
                # назва фігури в поточній позиції
                piece_name = value[0]
                # координати x, y поточної фігури
                piece_coord_x, piece_coord_y = value[2]
                # перевірити, чи є фігура на клітинці
                if (len(value[0]) > 1):
                    # намалювати фігуру на дошці
                    self.chess_pieces.draw(self.screen, piece_name,
                                           self.board_locations[piece_coord_x][piece_coord_y])

    # метод для пошуку можливих ходів вибраної фігури
    def possible_moves(self, piece_name, piece_coord):
        # список для збереження можливих ходів вибраної фігури
        positions = []
        # знайти можливі позиції для фігури
        if len(piece_name) > 0:
            # отримати координати x, y
            x_coord, y_coord = piece_coord

            # обчислити ходи для слона
            if piece_name[6:] == "bishop":
                positions = self.diagonal_moves(positions, piece_name, piece_coord)

            # обчислити ходи для пішака
            elif piece_name[6:] == "pawn":
                columnChar = chr(97 + x_coord)
                rowNo = 8 - y_coord

                # розрахувати ходи для чорного пішака
                if piece_name == "black_pawn":
                    if y_coord + 1 < 8:
                        front_piece = self.piece_location[columnChar][rowNo - 1][0]
                        if (front_piece == ""):
                            positions.append([x_coord, y_coord + 1])
                            if y_coord == 1:
                                if self.piece_location[columnChar][rowNo - 2][0] == "":
                                    positions.append([x_coord, y_coord + 2])

                        # взяття на проході / діагональ вліво
                        if x_coord - 1 >= 0 and y_coord + 1 < 8:
                            x = x_coord - 1
                            y = y_coord + 1
                            col_char = chr(97 + x)
                            r_no = 8 - y
                            to_capture = self.piece_location[col_char][r_no]
                            if (to_capture[0][:5] == "white"):
                                positions.append([x, y])

                        # діагональ вправо
                        if x_coord + 1 < 8 and y_coord + 1 < 8:
                            x = x_coord + 1
                            y = y_coord + 1
                            col_char = chr(97 + x)
                            r_no = 8 - y
                            to_capture = self.piece_location[col_char][r_no]
                            if (to_capture[0][:5] == "white"):
                                positions.append([x, y])

                # розрахувати ходи для білого пішака
                elif piece_name == "white_pawn":
                    if y_coord - 1 >= 0:
                        front_piece = self.piece_location[columnChar][rowNo + 1][0]
                        if (front_piece == ""):
                            positions.append([x_coord, y_coord - 1])
                            if y_coord == 6:
                                if self.piece_location[columnChar][rowNo + 2][0] == "":
                                    positions.append([x_coord, y_coord - 2])

                        # діагональ вліво
                        if x_coord - 1 >= 0 and y_coord - 1 >= 0:
                            x = x_coord - 1
                            y = y_coord - 1
                            col_char = chr(97 + x)
                            r_no = 8 - y
                            to_capture = self.piece_location[col_char][r_no]
                            if (to_capture[0][:5] == "black"):
                                positions.append([x, y])

                        # діагональ вправо
                        if x_coord + 1 < 8 and y_coord - 1 >= 0:
                            x = x_coord + 1
                            y = y_coord - 1
                            col_char = chr(97 + x)
                            r_no = 8 - y
                            to_capture = self.piece_location[col_char][r_no]
                            if (to_capture[0][:5] == "black"):
                                positions.append([x, y])

            # обчислити ходи для тури
            elif piece_name[6:] == "rook":
                positions = self.linear_moves(positions, piece_name, piece_coord)

            # обчислити ходи для коня
            elif piece_name[6:] == "knight":
                if (x_coord - 2) >= 0:
                    if (y_coord - 1) >= 0:
                        positions.append([x_coord - 2, y_coord - 1])
                    if (y_coord + 1) < 8:
                        positions.append([x_coord - 2, y_coord + 1])
                if (y_coord - 2) >= 0:
                    if (x_coord - 1) >= 0:
                        positions.append([x_coord - 1, y_coord - 2])
                    if (x_coord + 1) < 8:
                        positions.append([x_coord + 1, y_coord - 2])
                if (x_coord + 2) < 8:
                    if (y_coord - 1) >= 0:
                        positions.append([x_coord + 2, y_coord - 1])
                    if (y_coord + 1) < 8:
                        positions.append([x_coord + 2, y_coord + 1])
                if (y_coord + 2) < 8:
                    if (x_coord - 1) >= 0:
                        positions.append([x_coord - 1, y_coord + 2])
                    if (x_coord + 1) < 8:
                        positions.append([x_coord + 1, y_coord + 2])

            # обчислити ходи для короля
            elif piece_name[6:] == "king":
                # Стандартні ходи на 1 клітинку навколо короля
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x_coord + dx, y_coord + dy
                        if 0 <= nx < 8 and 0 <= ny < 8:
                            positions.append([nx, ny])

                # --- РОКІРУВАННЯ ---
                is_black = (piece_name[:5] == "black")
                king_moved_key = "black_king" if is_black else "white_king"
                rook_a_key = "black_rook_a" if is_black else "white_rook_a"
                rook_h_key = "black_rook_h" if is_black else "white_rook_h"
                row_no_val = 8 if is_black else 1

                # Якщо король ще не ходив
                if not self.has_moved[king_moved_key]:
                    # 1. Коротка рокірування (праворуч, до тури 'h')
                    if not self.has_moved[rook_h_key]:
                        if self.piece_location['f'][row_no_val][0] == "" and self.piece_location['g'][row_no_val][
                            0] == "":
                            positions.append([6, y_coord])  # Колонка g (x=6)

                    # 2. Довга рокірування (ліворуч, до тури 'a')
                    if not self.has_moved[rook_a_key]:
                        if (self.piece_location['b'][row_no_val][0] == "" and
                                self.piece_location['c'][row_no_val][0] == "" and
                                self.piece_location['d'][row_no_val][0] == ""):
                            positions.append([2, y_coord])  # Колонка c (x=2)

            # обчислити ходи для ферзя
            elif piece_name[6:] == "queen":
                positions = self.diagonal_moves(positions, piece_name, piece_coord)
                positions = self.linear_moves(positions, piece_name, piece_coord)

            # список позицій для видалення
            to_remove = []

            # видалити позиції, які перекривають інші фігури поточного гравця
            for pos in positions:
                x, y = pos
                columnChar = chr(97 + x)
                rowNo = 8 - y

                des_piece_name = self.piece_location[columnChar][rowNo][0]
                if (des_piece_name[:5] == piece_name[:5]):
                    to_remove.append(pos)

            for i in to_remove:
                positions.remove(i)

        return positions

    def move_piece(self, turn):
        square = self.get_selected_square()

        if square:
            piece_name = square[0]
            piece_color = piece_name[:5]
            columnChar = square[1]
            rowNo = square[2]

            x, y = self.piece_location[columnChar][rowNo][2]

            if (len(piece_name) > 0) and (piece_color == turn):
                self.moves = self.possible_moves(piece_name, [x, y])

            p = self.piece_location[columnChar][rowNo]

            for i in self.moves:
                if i == [x, y]:
                    if (p[0][:5] == turn) or len(p[0]) == 0:
                        self.validate_move([x, y])
                    else:
                        self.capture_piece(turn, [columnChar, rowNo], [x, y])

            if (piece_color == turn):
                for k in self.piece_location.keys():
                    for key in self.piece_location[k].keys():
                        self.piece_location[k][key][1] = False

                self.piece_location[columnChar][rowNo][1] = True

    def get_selected_square(self):
        left_click = self.utils.left_click_event()

        if left_click:
            mouse_event = self.utils.get_mouse_event()

            for i in range(len(self.board_locations)):
                for j in range(len(self.board_locations)):
                    rect = pygame.Rect(self.board_locations[i][j][0], self.board_locations[i][j][1],
                                       self.square_length, self.square_length)
                    collision = rect.collidepoint(mouse_event[0], mouse_event[1])
                    if collision:
                        selected = [rect.x, rect.y]
                        for k in range(len(self.board_locations)):
                            try:
                                l = self.board_locations[k].index(selected)
                                if l is not None:
                                    for val in self.piece_location.values():
                                        for value in val.values():
                                            if not value[1]:
                                                value[1] = False

                                    columnChar = chr(97 + k)
                                    rowNo = 8 - l
                                    piece_name = self.piece_location[columnChar][rowNo][0]

                                    return [piece_name, columnChar, rowNo]
                            except:
                                pass
        else:
            return None

    def capture_piece(self, turn, chess_board_coord, piece_coord):
        # Отримуємо фігуру, яка стоїть НА КЛІТИНЦІ ПРИЗНАЧЕННЯ (яку атакують)
        desColChar = chr(97 + piece_coord[0])
        desRowNo = 8 - piece_coord[1]
        target_piece = self.piece_location[desColChar][desRowNo][0]

        # Якщо з'їли короля супротивника — перемагає той, хто ходив
        if target_piece == "white_king":
            self.winner = "Black"
            print("Black wins")
        elif target_piece == "black_king":
            self.winner = "White"
            print("White wins")

        # Додаємо з'їдену фігуру в список захоплених
        captured_piece = self.piece_location[desColChar][desRowNo]
        self.captured.append(captured_piece)

        # Виконуємо хід
        self.validate_move(piece_coord)

    def validate_move(self, destination):
        random.choice(move_sounds).play()
        desColChar = chr(97 + destination[0])
        desRowNo = 8 - destination[1]

        for k in self.piece_location.keys():
            for key in self.piece_location[k].keys():
                board_piece = self.piece_location[k][key]

                if board_piece[1]:
                    # скасувати вибір вихідної фігури
                    self.piece_location[k][key][1] = False
                    piece_name = self.piece_location[k][key][0]

                    # Обробка рокірування для короля
                    if piece_name == "white_king" or piece_name == "black_king":
                        dx = destination[0] - (ord(k) - 97)
                        if abs(dx) == 2:
                            row_char = 1 if piece_name[:5] == "white" else 8
                            if destination[0] == 6:  # Коротка рокірування (праворуч)
                                rook_name = self.piece_location['h'][row_char][0]
                                self.piece_location['f'][row_char][0] = rook_name
                                self.piece_location['h'][row_char][0] = ""
                            elif destination[0] == 2:  # Довга рокірування (ліворуч)
                                rook_name = self.piece_location['a'][row_char][0]
                                self.piece_location['d'][row_char][0] = rook_name
                                self.piece_location['a'][row_char][0] = ""

                    # перемістити вихідну фігуру на кінцеву позицію
                    self.piece_location[desColChar][desRowNo][0] = piece_name

                    src_name = self.piece_location[k][key][0]
                    self.piece_location[k][key][0] = ""

                    # змінити чергу ходу
                    if (self.turn["black"]):
                        self.turn["black"] = 0
                        self.turn["white"] = 1
                    else:
                        self.turn["black"] = 1
                        self.turn["white"] = 0

                    src_location = k + str(key)
                    des_location = desColChar + str(desRowNo)
                    print("{} moved from {} to {}".format(src_name, src_location, des_location))

                    # Оновлення прапорців переміщення для короля та тур (для рокірування)
                    if piece_name == "white_king":
                        self.has_moved["white_king"] = True
                    elif piece_name == "black_king":
                        self.has_moved["black_king"] = True
                    elif piece_name == "white_rook":
                        if k == 'a':
                            self.has_moved["white_rook_a"] = True
                        elif k == 'h':
                            self.has_moved["white_rook_h"] = True
                    elif piece_name == "black_rook":
                        if k == 'a':
                            self.has_moved["black_rook_a"] = True
                        elif k == 'h':
                            self.has_moved["black_rook_h"] = True

    # допоміжна функція для пошуку діагональних ходів
    def diagonal_moves(self, positions, piece_name, piece_coord):
        x, y = piece_coord
        # верхні ліві діагональні позиції
        while (True):
            x = x - 1
            y = y - 1
            if (x < 0 or y < 0):
                break
            else:
                positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        x, y = piece_coord
        # нижні праві діагональні позиції
        while (True):
            x = x + 1
            y = y + 1
            if (x > 7 or y > 7):
                break
            else:
                positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        x, y = piece_coord
        # нижні ліві діагональні позиції
        while (True):
            x = x - 1
            y = y + 1
            if (x < 0 or y > 7):
                break
            else:
                positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        x, y = piece_coord
        # верхні праві діагональні позиції
        while (True):
            x = x + 1
            y = y - 1
            if (x > 7 or y < 0):
                break
            else:
                positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        return positions

    # допоміжна функція для пошуку горизонтальних і вертикальних ходів
    def linear_moves(self, positions, piece_name, piece_coord):
        x, y = piece_coord
        # горизонтальні ходи вліво
        while (x > 0):
            x = x - 1
            positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        x, y = piece_coord
        # горизонтальні ходи вправо
        while (x < 7):
            x = x + 1
            positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        x, y = piece_coord
        # вертикальні ходи вгору
        while (y > 0):
            y = y - 1
            positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        x, y = piece_coord
        # вертикальні ходи вниз
        while (y < 7):
            y = y + 1
            positions.append([x, y])

            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            if len(p[0]) > 0 and piece_name[:5] != p[0][:5]:
                break
            elif len(p[0]) > 0:
                break

        return positions