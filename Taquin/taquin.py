#! /usr/bin/python
# -*- coding: utf-8 -*-

"""'15 Puzzle ('Magic 15') Game"""

import os
import tkinter
from random import randrange
from itertools import product
from typing import Callable, Tuple, TypeAlias
from collections import OrderedDict


import numpy as np

Position: TypeAlias = Tuple[int, int]


class Img:

    def __init__(self, file: str):
        self.img = tkinter.PhotoImage(file=file)


class Tile:
    """Puzzle tile"""
    def __init__(self, true_pos: Position, img: Img, text: str,
                 command: Callable, size: int = 200):
        self.text = text
        self.img = img
        self.btn_tile = tkinter.Button(text=text,
                                       command=lambda: command(self),
                                       image=self.img.img)
        self.size = size
        self.current_pos = None
        self.true_pos = true_pos

    def move(self, pos: Position):
        self.btn_tile.place(x=pos[0]*self.size, y=pos[1]*self.size)

    def __str__(self):
        return f"Tile({self.text}, {self.true_pos})"


class Puzzle:
    """Puzzle : stores the tiles, moves them, etc."""
    def __init__(self, d_name_and_file: dict[str, str],
                 shape: Tuple[int, int] = (4, 4), tile_size: int = 200):
        self.tiles = np.empty(shape, dtype=object)
        self.shape = shape
        l_pos = self.init_puzzle_pos()
        if len(d_name_and_file) != len(l_pos) - 1:
            raise ValueError("The number of files must match w*h-1")
        for pos, (name, file) in zip(l_pos, d_name_and_file.items()):
            img = Img(file)
            self.tiles[pos] = Tile(pos, img, name, command=self.click,
                                   size=tile_size)
        self.empty = l_pos[-1]
        self.tile_size = tile_size
        self.draw_all()

    def init_puzzle_pos(self) -> list[Position]:
        w, h = self.shape
        ll = list(product(range(w), range(h)))
        ll.sort(key=lambda pos: (pos[1], pos[0]))
        return ll

    def can_move(self, pos: Position) -> bool:
        x, y = pos
        x_empty, y_empty = self.empty
        return (x == x_empty and abs(y - y_empty) == 1) \
            or (y == y_empty and abs(x - x_empty) == 1)

    def is_valid_pos(self, pos: Position) -> bool:
        w, h = self.shape
        row, col = pos
        return 0 <= row < w and 0 <= col < h

    def click(self, tile: Tile):
        pos = tile.current_pos
        if not self.can_move(pos):
            return
        self.move_pos(pos)

    def tiles_can_move(self) -> list[Position]:
        """Returns the list of pos where a tile can move"""
        x_empty, y_empty = self.empty
        l_tiles = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            pos = (x_empty + dx, y_empty + dy)
            if self.is_valid_pos(pos):
                l_tiles.append(pos)
        return l_tiles

    def move_pos(self, pos: Position) -> None:
        """manages the move of a tile at `pos`"""
        tile: Tile = self.tiles[pos]
        move_pos = self.empty
        self.tiles[pos] = None
        self.empty = pos

        self.tiles[move_pos] = tile
        tile.move(move_pos)

        tile.current_pos = move_pos

    def shuffle(self, nb_shuffle=2):
        """Shuffles the puzzle"""
        for _ in range(nb_shuffle):
            can_move_pos = self.tiles_can_move()
            count = len(can_move_pos)
            jj = randrange(0, count)
            pos = can_move_pos[jj]
            self.move_pos(pos)

    def draw_all(self):
        for row, col in np.ndindex(*self.shape):
            tile = self.tiles[row, col]
            if tile is None:
                continue
            if not isinstance(tile, Tile):
                raise ValueError
            tile.move((row, col))

    def is_end(self):
        for row, col in np.ndindex(*self.shape):
            if self.tiles[row, col] is None:
                continue
            if self.tiles[row, col].true_pos != (row, col):
                return False
        return True


class PuzzleGame:
    """Main Puzzle Game: initiate the puzzle, manages the main window"""

    _names_and_files = OrderedDict([
        ("1", "1.gif"), ("2", "2.gif"), ("3", "3.gif"), ("4", "4.gif"),
        ("5", "5.gif"), ("6", "6.gif"), ("7", "7.gif"), ("8", "8.gif"),
        ("9", "9.gif"), ("10", "10.gif"), ("11", "11.gif"), ("12", "12.gif"),
        ("13", "13.gif"), ("14", "14.gif"), ("15", "15.gif")])
    _shape = (4, 4)
    _tile_size = 200
    _done_puzzle_file = "img/Taquin.gif"
    _shuffle = 1000  # 1000

    def __init__(self, path: str = ""):
        names_and_files = {name: f"{path}img/{self._names_and_files[name]}"
                           for name in self._names_and_files}

        self.main_window = tkinter.Tk()
        self.main_window.title("Project Magic 15")
        w, h = self._shape
        self.set_geometry(self.main_window, width=w * self._tile_size,
                          height=h * self._tile_size)

        self.puzzle = Puzzle(names_and_files, self._shape,
                             self._tile_size)

        self.done_img = Img(path+self._done_puzzle_file)

        self.main_window.bind("<ButtonRelease-1>", self.event_after_move)
        # lorsque l'on relâche le clic droit, on lance la détection.

        self.puzzle.shuffle(nb_shuffle=self._shuffle)
        self.puzzle.draw_all()

    def done_label(self):
        """Makes a label displaying the finished puzzle."""
        return tkinter.Label(self.main_window, image=self.done_img.img)

    @staticmethod
    def set_geometry(window, width: int, height: int) -> None:
        """Set the geometry of the window, and centers it on the screen"""
        w_screen = window.winfo_screenwidth()
        h_screen = window.winfo_screenheight()
        x_ = (w_screen - width) // 2
        y_ = (h_screen - height) // 2
        window.geometry(f'{width}x{height}+{x_}+{y_}')

    def event_after_move(self, _: tkinter.Event):
        """Manages - if necessary - the victory"""
        if not self.puzzle.is_end():
            return
        self.victory()

    def victory(self) -> None:
        """The player has won. Handles the application"""
        end_window = tkinter.Toplevel(self.main_window)
        win_label = tkinter.Label(end_window,
                                  text="Félicitations vous avez réussi !")
        end_button = tkinter.Button(end_window, text="OK",
                                    command=end_window.destroy)
        self.done_label().place(x=0, y=0)
        # create a window to notify the player and display the uncut image
        self.set_geometry(end_window, 200, 50)
        # on centre la fenêtre

        win_label.pack()
        end_button.pack()
        # on affiche la fenêtre de notification et son contenu

    def mainloop(self):
        self.main_window.mainloop()


def main():
    folder = os.path.dirname(__file__)
    game = PuzzleGame(path=f"{folder}/")
    game.mainloop()


if __name__ == "__main__":
    main()
