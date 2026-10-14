import pygame
from pygame.locals import *
import random

from piece import Piece
from utils import Utils

import time

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
            "white_pawn":   5,
            "white_knight": 3,
            "white_bishop": 2,
            "white_rook":   4,
            "white_king":   0,
            "white_queen":  1,
            "black_pawn":   11,
            "black_knight": 9,
            "black_bishop": 8,
            "black_rook":   10,
            "black_king":   6,
            "black_queen":  7
        }

        # список захоплених фігур
        self.captured = []
        #
        self.winner = ""

        self.reset()


        # Словник для відстеження, чи робили король або тури ходи (потрібно для рокірування)
        self.has_moved = {
            "white_king": False,
            "white_rook_a": False,  # тура на лінії 'a' (довга рокірування)
            "white_rook_h": False,  # тура на лінії 'h' (коротка рокірування)
            "black_king": False,
            "black_rook_a": False,
            "black_rook_h": False
        }

    def reset(self):
        # очистити список ходів
        self.moves = []

        # випадковим чином визначити черговість ходу гравця
        x = random.randint(0, 1)
        if(x == 1):
            self.turn["black"] = 1
        elif(x == 0):
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
                if(x == 8):
                    if(chr(i) == 'a' or chr(i) == 'h'):
                        self.piece_location[chr(i)][x][0] = "black_rook"
                    elif(chr(i) == 'b' or chr(i) == 'g'):
                        self.piece_location[chr(i)][x][0] = "black_knight"
                    elif(chr(i) == 'c' or chr(i) == 'f'):
                        self.piece_location[chr(i)][x][0] = "black_bishop"
                    elif(chr(i) == 'd'):
                        self.piece_location[chr(i)][x][0] = "black_queen"
                    elif(chr(i) == 'e'):
                        self.piece_location[chr(i)][x][0] = "black_king"
                elif(x == 7):
                    self.piece_location[chr(i)][x][0] = "black_pawn"
                elif(x == 2):
                    self.piece_location[chr(i)][x][0] = "white_pawn"
                elif(x == 1):
                    if(chr(i) == 'a' or chr(i) == 'h'):
                        self.piece_location[chr(i)][x][0] = "white_rook"
                    elif(chr(i) == 'b' or chr(i) == 'g'):
                        self.piece_location[chr(i)][x][0] = "white_knight"
                    elif(chr(i) == 'c' or chr(i) == 'f'):
                        self.piece_location[chr(i)][x][0] = "white_bishop"
                    elif(chr(i) == 'd'):
                        self.piece_location[chr(i)][x][0] = "white_queen"
                    elif(chr(i) == 'e'):
                        self.piece_location[chr(i)][x][0] = "white_king"
                x = x - 1


    #
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
                       ((self.screen.get_width() - turn_text.get_width()) // 2,
                      10))

        # дозволити грати гравцю з чорними фігурами
        if(self.turn["black"]):
            self.move_piece("black")
        # дозволити грати гравцю з білими фігурами
        elif(self.turn["white"]):
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
                if(len(value[0]) > 1):
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
                # перетворити індекс списку на ключ словника
                columnChar = chr(97 + x_coord)
                rowNo = 8 - y_coord

                # розрахувати ходи для чорного пішака
                if piece_name == "black_pawn":
                    if y_coord + 1 < 8:
                        # отримати рядок перед чорним пішаком
                        rowNo = rowNo - 1
                        front_piece = self.piece_location[columnChar][rowNo][0]

                        # пішаки не можуть рухатися, якщо заблоковані іншим пішаком
                        if(front_piece[6:] != "pawn"):
                            positions.append([x_coord, y_coord+1])
                            # чорні пішаки можуть рухатися на дві позиції вперед при першому ході
                            if y_coord < 2:
                                positions.append([x_coord, y_coord+2])

                        # В ПРОХОДІ (EN PASSANT)
                        # діагональ вліво
                        if x_coord - 1 >= 0 and y_coord + 1 < 8:
                            x = x_coord - 1
                            y = y_coord + 1

                            # перетворити індекс списку на ключ словника
                            columnChar = chr(97 + x)
                            rowNo = 8 - y
                            to_capture = self.piece_location[columnChar][rowNo]

                            if(to_capture[0][:5] == "white"):
                                positions.append([x, y])

                        # діагональ вправо
                        if x_coord + 1 < 8 and y_coord + 1 < 8:
                            x = x_coord + 1
                            y = y_coord + 1

                            # перетворити індекс списку на ключ словника
                            columnChar = chr(97 + x)
                            rowNo = 8 - y
                            to_capture = self.piece_location[columnChar][rowNo]

                            if(to_capture[0][:5] == "white"):
                                positions.append([x, y])

                # розрахувати ходи для білого пішака
                elif piece_name == "white_pawn":
                    if y_coord - 1 >= 0:
                        # отримати рядок перед білим пішаком
                        rowNo = rowNo + 1
                        front_piece = self.piece_location[columnChar][rowNo][0]

                        # пішаки не можуть рухатися, якщо заблоковані іншим пішаком
                        if(front_piece[6:] != "pawn"):
                            positions.append([x_coord, y_coord-1])
                            # білі пішаки можуть рухатися на дві позиції вперед при першому ході
                            if y_coord > 5:
                                positions.append([x_coord, y_coord-2])

                        # В ПРОХОДІ (EN PASSANT)
                        # діагональ вліво
                        if x_coord - 1 >= 0 and y_coord - 1 >= 0:
                            x = x_coord - 1
                            y = y_coord - 1

                            # перетворити індекс списку на ключ словника
                            columnChar = chr(97 + x)
                            rowNo = 8 - y
                            to_capture = self.piece_location[columnChar][rowNo]

                            if(to_capture[0][:5] == "black"):
                                positions.append([x, y])

                        # діагональ вправо
                        if x_coord + 1 < 8 and y_coord - 1 >= 0:
                            x = x_coord + 1
                            y = y_coord - 1

                            # перетворити індекс списку на ключ словника
                            columnChar = chr(97 + x)
                            rowNo = 8 - y
                            to_capture = self.piece_location[columnChar][rowNo]

                            if(to_capture[0][:5] == "black"):
                                positions.append([x, y])


            # обчислити ходи для тури
            elif piece_name[6:] == "rook":
                # знайти лінійні ходи
                positions = self.linear_moves(positions, piece_name, piece_coord)

            # обчислити ходи для коня
            elif piece_name[6:] == "knight":
                # ліві позиції
                if(x_coord - 2) >= 0:
                    if(y_coord - 1) >= 0:
                        positions.append([x_coord-2, y_coord-1])
                    if(y_coord + 1) < 8:
                        positions.append([x_coord-2, y_coord+1])
                # верхні позиції
                if(y_coord - 2) >= 0:
                    if(x_coord - 1) >= 0:
                        positions.append([x_coord-1, y_coord-2])
                    if(x_coord + 1) < 8:
                        positions.append([x_coord+1, y_coord-2])
                # праві позиції
                if(x_coord + 2) < 8:
                    if(y_coord - 1) >= 0:
                        positions.append([x_coord+2, y_coord-1])
                    if(y_coord + 1) < 8:
                        positions.append([x_coord+2, y_coord+1])
                # нижні позиції
                if(y_coord + 2) < 8:
                    if(x_coord - 1) >= 0:
                        positions.append([x_coord-1, y_coord+2])
                    if(x_coord + 1) < 8:
                        positions.append([x_coord+1, y_coord+2])

            # обчислити ходи для короля
            elif piece_name[6:] == "king":
                if(y_coord - 1) >= 0:
                    # верхня позиція
                    positions.append([x_coord, y_coord-1])

                if(y_coord + 1) < 8:
                    # нижня позиція
                    positions.append([x_coord, y_coord+1])

                if(x_coord - 1) >= 0:
                    # ліва позиція
                    positions.append([x_coord-1, y_coord])
                    # верхня ліва позиція
                    if(y_coord - 1) >= 0:
                        positions.append([x_coord-1, y_coord-1])
                    # нижня ліва позиція
                    if(y_coord + 1) < 8:
                        positions.append([x_coord-1, y_coord+1])

                if(x_coord + 1) < 8:
                    # права позиція
                    positions.append([x_coord+1, y_coord])
                    # верхня права позиція
                    if(y_coord - 1) >= 0:
                        positions.append([x_coord+1, y_coord-1])
                    # нижня права позиція
                    if(y_coord + 1) < 8:
                        positions.append([x_coord+1, y_coord+1])

                        # Перевірка для короля
                        elif piece_name[6:] == "king":
                        # (тут залишаються ваші стандартні сусідні клітинки короля...)

                        # --- РОКІРУВАННЯ ---
                        is_black = (piece_name[:5] == "black")
                        king_moved_key = "black_king" if is_black else "white_king"
                        rook_a_key = "black_rook_a" if is_black else "white_rook_a"
                        rook_h_key = "black_rook_h" if is_black else "white_rook_h"

                        # Якщо король ще не ходив
                        if not self.has_moved[king_moved_key]:
                            # 1. Коротка рокірування (праворуч, до тури 'h')
                            if not self.has_moved[rook_h_key]:
                                # Перевіряємо, чи порожні клітинки між королем (x=4) і турою (x=7) -> колонки f (x=5) та g (x=6)
                                if self.piece_location['f'][rowNo][0] == "" and self.piece_location['g'][rowNo][
                                    0] == "":
                                    positions.append(
                                        [6, y_coord])  # Король переміщується на двома клітинками вправо (колонку g)

                            # 2. Довга рокірування (ліворуч, до тури 'a')
                            if not self.has_moved[rook_a_key]:
                                # Перевіряємо клітинки b, c, d -> колонки 1, 2, 3 (або b, c, d)
                                if (self.piece_location['b'][rowNo][0] == "" and
                                        self.piece_location['c'][rowNo][0] == "" and
                                        self.piece_location['d'][rowNo][0] == ""):
                                    positions.append(
                                        [2, y_coord])  # Король переміщується на дві клітинки вліво (колонку c)

            # обчислити ходи для ферзя
            elif piece_name[6:] == "queen":
                # знайти діагональні позиції
                positions = self.diagonal_moves(positions, piece_name, piece_coord)

                # знайти лінійні ходи
                positions = self.linear_moves(positions, piece_name, piece_coord)

            # список позицій для видалення
            to_remove = []

            # видалити позиції, які перекривають інші фігури поточного гравця
            for pos in positions:
                x, y = pos

                # перетворити індекс списку на ключ словника
                columnChar = chr(97 + x)
                rowNo = 8 - y

                # знайти фігури для видалення
                des_piece_name = self.piece_location[columnChar][rowNo][0]
                if(des_piece_name[:5] == piece_name[:5]):
                    to_remove.append(pos)

            # видалити позицію зі списку можливих ходів
            for i in to_remove:
                positions.remove(i)

        # повернути список, що містить можливі ходи для вибраної фігури
        return positions



    def move_piece(self, turn):
        # отримати координати клітинки, вибраної на дошці
        square = self.get_selected_square()

        # якщо клітинка була вибрана
        if square:
            # отримати назву фігури на вибраній клітинці
            piece_name = square[0]
            # колір фігури на вибраній клітинці
            piece_color = piece_name[:5]
            # символ стовпця дошки
            columnChar = square[1]
            # номер рядка дошки
            rowNo = square[2]

            # отримати координати x, y
            x, y = self.piece_location[columnChar][rowNo][2]

            # якщо на вибраній клітинці є фігура і це колір поточного гравця
            if(len(piece_name) > 0) and (piece_color == turn):
                # знайти можливі ходи для фігури
                self.moves = self.possible_moves(piece_name, [x, y])

            # механізм перевірки шаху/мату
            p = self.piece_location[columnChar][rowNo]

            for i in self.moves:
                if i == [x, y]:
                    if(p[0][:5] == turn) or len(p[0]) == 0:
                        self.validate_move([x, y])
                    else:
                        self.capture_piece(turn, [columnChar, rowNo], [x, y])

            # ходити може лише гравець, чия черга
            if(piece_color == turn):
                # зняти прапорець вибору з усіх інших фігур
                for k in self.piece_location.keys():
                    for key in self.piece_location[k].keys():
                        self.piece_location[k][key][1] = False

                # встановити прапорець вибору для вибраної фігури
                self.piece_location[columnChar][rowNo][1] = True


    def get_selected_square(self):
        # отримати подію натискання лівої кнопки миші
        left_click = self.utils.left_click_event()

        # якщо є подія миші
        if left_click:
            # отримати саму подію миші
            mouse_event = self.utils.get_mouse_event()

            for i in range(len(self.board_locations)):
                for j in range(len(self.board_locations)):
                    rect = pygame.Rect(self.board_locations[i][j][0], self.board_locations[i][j][1],
                            self.square_length, self.square_length)
                    collision = rect.collidepoint(mouse_event[0], mouse_event[1])
                    if collision:
                        selected = [rect.x, rect.y]
                        # знайти координати x, y вибраної клітинки
                        for k in range(len(self.board_locations)):
                            #
                            try:
                                l = None
                                l = self.board_locations[k].index(selected)
                                if l != None:
                                    # скинути колір усіх вибраних фігур
                                    for val in self.piece_location.values():
                                        for value in val.values():
                                            # [назва фігури, чи вибрана зараз, координати на дошці]
                                            if not value[1]:
                                                value[1] = False

                                    # отримати символ стовпця та номер рядка шахової фігури
                                    columnChar = chr(97 + k)
                                    rowNo = 8 - l
                                    # отримати назву фігури
                                    piece_name = self.piece_location[columnChar][rowNo][0]

                                    return [piece_name, columnChar, rowNo]
                            except:
                                pass
        else:
            return None


    def capture_piece(self, turn, chess_board_coord, piece_coord):
        # отримати координати x, y цільової фігури
        x, y = piece_coord

        # отримати координати шахівниці
        columnChar, rowNo = chess_board_coord

        p = self.piece_location[columnChar][rowNo]

        if p[0] == "white_king":
            self.winner = "Black"
            print("Black wins")
        elif p[0] == "black_king":
            self.winner = "White"
            print("White wins")

        # додати захоплену фігуру до списку
        self.captured.append(p)
        # перемістити вихідну фігуру до пункту призначення
        self.validate_move(piece_coord)


    def validate_move(self, destination):
        desColChar = chr(97 + destination[0])
        desRowNo = 8 - destination[1]

        for k in self.piece_location.keys():
            for key in self.piece_location[k].keys():
                board_piece = self.piece_location[k][key]

                # Усередині validate_move, після переміщення короля:
                if piece_name == "white_king" or piece_name == "black_king":
                    # Якщо різниця по координаті X дорівнює 2, це рокірування!
                    dx = destination[0] - k_old_x  # (потрібно зберегти старий x короля перед переміщенням)
                    if abs(dx) == 2:
                        row_char = '1' if piece_name[:5] == "white" else '8'
                        if destination[0] == 6:  # Коротка рокірування (праворуч)
                            # Тура переміщується з h на f (колонка 7 на 5)
                            rook_name = self.piece_location['h'][int(row_char)][0]
                            self.piece_location['f'][int(row_char)][0] = rook_name
                            self.piece_location['h'][int(row_char)][0] = ""
                        elif destination[0] == 2:  # Довга рокірування (ліворуч)
                            # Тура переміщується з a на d (колонка 0 на 3)
                            rook_name = self.piece_location['a'][int(row_char)][0]
                            self.piece_location['d'][int(row_char)][0] = rook_name
                            self.piece_location['a'][int(row_char)][0] = ""

                if board_piece[1]:
                    # скасувати вибір вихідної фігури
                    self.piece_location[k][key][1] = False
                    # отримати назву вихідної фігури
                    piece_name = self.piece_location[k][key][0]
                    # перемістити вихідну фігуру на кінцеву позицію
                    self.piece_location[desColChar][desRowNo][0] = piece_name

                    src_name = self.piece_location[k][key][0]
                    # видалити вихідну фігуру з її поточної позиції
                    self.piece_location[k][key][0] = ""

                    # змінити чергу ходу
                    if(self.turn["black"]):
                        self.turn["black"] = 0
                        self.turn["white"] = 1
                    elif("white"):
                        self.turn["black"] = 1
                        self.turn["white"] = 0

                    src_location = k + str(key)
                    des_location = desColChar + str(desRowNo)
                    print("{} moved from {} to {}".format(src_name, src_location, des_location))

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
        # скинути значення координат x та y
        x, y = piece_coord
        # знайти верхні ліві діагональні позиції
        while(True):
            x = x - 1
            y = y - 1
            if(x < 0 or y < 0):
                break
            else:
                positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break

        # скинути значення координат x та y
        x, y = piece_coord
        # знайти нижні праві діагональні позиції
        while(True):
            x = x + 1
            y = y + 1
            if(x > 7 or y > 7):
                break
            else:
                positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break

        # скинути значення координат x та y
        x, y = piece_coord
        # знайти нижні ліві діагональні позиції
        while(True):
            x = x - 1
            y = y + 1
            if (x < 0 or y > 7):
                break
            else:
                positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break

        # скинути значення координат x та y
        x, y = piece_coord
        # знайти верхні праві діагональні позиції
        while(True):
            x = x + 1
            y = y - 1
            if(x > 7 or y < 0):
                break
            else:
                positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break

        return positions


    # допоміжна функція для пошуку горизонтальних і вертикальних ходів
    def linear_moves(self, positions, piece_name, piece_coord):
        # скинути значення координат x, y
        x, y = piece_coord
        # горизонтальні ходи вліво
        while(x > 0):
            x = x - 1
            positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break


        # скинути значення координат x, y
        x, y = piece_coord
        # горизонтальні ходи вправо
        while(x < 7):
            x = x + 1
            positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break

        # скинути значення координат x, y
        x, y = piece_coord
        # вертикальні ходи вгору
        while(y > 0):
            y = y - 1
            positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break

        # скинути значення координат x, y
        x, y = piece_coord
        # вертикальні ходи вниз
        while(y < 7):
            y = y + 1
            positions.append([x, y])

            # перетворити індекс списку на ключ словника
            columnChar = chr(97 + x)
            rowNo = 8 - y
            p = self.piece_location[columnChar][rowNo]

            # зупинити пошук можливих ходів, якщо шлях заблоковано фігурою
            if len(p[0]) > 0 and piece_name[:5] != p[:5]:
                break


        return positions