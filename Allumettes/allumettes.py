#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Game of Nim with matches"""

import turtle
import tkinter

PATH = ""  # "Allumettes/"
MATCH_SYMBOL = "match_symbol.gif"
BG_IMG = "lighted_match.gif"  # background img


def set_geometry(window, width: int, height: int) -> None:
    """Set the geometry of the window, and centers it on the screen"""
    w_screen = window.winfo_screenwidth()
    h_screen = window.winfo_screenheight()
    x_ = (w_screen - width) // 2
    y_ = (h_screen - height) // 2
    window.geometry(f'{width}x{height}+{x_}+{y_}')


class NimGame:
    """Game of Nim"""

    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Matches: Game of Nim")

        set_geometry(self.window, 800, 600)

        canvas1 = tkinter.Canvas(self.window, width=800, height=600)
        canvas1.pack()
        screen1 = turtle.TurtleScreen(canvas1)

        screen1.register_shape(PATH + MATCH_SYMBOL)
        screen1.bgpic(PATH + BG_IMG)

        # The `nb_remaining` attribute represents the number of matches left
        #  in play, when it is 0, the second last player is the winner."""
        self.nb_remaining = 16

        # Creation of the 16 cursors which will have the image of a match.
        #  We place them in a list in order to facilitate their management
        #  (assigning them the image of the match,
        #  placing them in the right place, etc.)
        self.list_matchstick = [turtle.RawTurtle(screen1) for _ in range(16)]
        for i in self.list_matchstick:
            i.shape(PATH + MATCH_SYMBOL)

        self.state_player = tkinter.IntVar()
        self.row_select = tkinter.IntVar()

        self.init_place_matches()

        self.new_game()

        for i in self.list_matchstick:
            i.onclick(self.remove, btn=1)

        # Création des 2 boutons radio pour changer de joueur
        # et du bouton recommencer
        player_1 = tkinter.Radiobutton(
            text="Joueur 1", variable=self.state_player, value=2,
            command=lambda: [self.row_select.set(-1)])
        player_2 = tkinter.Radiobutton(
            text="Joueur 2", variable=self.state_player, value=1,
            command=lambda: [self.row_select.set(-1)])
        restart = tkinter.Button(text="New game", command=self.new_game)

        # placing the buttons
        player_1.place(x=150, y=100)
        player_2.place(x=150, y=150)
        restart.place(x=150, y=200)

    def init_place_matches(self) -> None:
        # the list contains the positions of each match,
        # to form the shape of a triangle
        triangle_toto = [[0, 210], [-30, 140], [0, 140], [30, 140], [-60, 70],
                         [-30, 70], [0, 70], [30, 70], [60, 70], [-90, 0],
                         [-60, 0], [-30, 0], [0, 0], [30, 0], [60, 0], [90, 0]]

        # Moving the matches at the right place
        for match, position in zip(self.list_matchstick, triangle_toto):
            match.up()
            match.goto(position)
            match.down()

    def mainloop(self):
        self.window.mainloop()

    def win(self):
        if self.nb_remaining != 0:
            return
        window2 = tkinter.Toplevel(self.window)
        msg = tkinter.Label(
            window2, text=f"Congratulations Player {self.state_player.get()},"
                          f" you've won !!!")
        msg.pack()
        ok_btn = tkinter.Button(window2, text="OK",
                                command=window2.destroy)
        ok_btn.pack()

        set_geometry(window2, 300, 50)

    def new_game(self):
        """Resets the variables in order to play a new game"""
        self.nb_remaining = 16
        self.state_player.set(2)
        self.row_select.set(-1)
        for match in self.list_matchstick:
            match.st()

    def remove(self, x, y):
        """Allows a match to be deleted depending on several things.

        First of course if the player clicks on a match,
         secondly if he has not already deleted a match from another row
         during his turn."""
        a = [x, y]
        for match in self.list_matchstick:
            z = match.pos()
            if (abs(a[0] - z[0]) < 10 and abs(a[1] - z[1]) < 25) and (
                    self.row_select.get() == -1
                    or z[1] == self.row_select.get()):
                match.ht()
                self.nb_remaining -= 1
                self.win()
                if self.row_select.get() == -1:
                    self.row_select.set(int(z[1]))


if __name__ == "__main__":
    NimGame().mainloop()
