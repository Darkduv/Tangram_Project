#! /usr/bin/python
# -*- coding: utf-8 -*-
# ######### Allumettes ###########

from turtle import *
from tkinter import *


# Fonction qui permet d'autoriser l'effaçage d'une allumette en fonction de plusieurs choses,
# tout d'abord bien sur si le joueur clique sur une allumette, et ensuite s'il n'a pas déjà
# effacé pendant son tour une allumette d'un autre étage.

def efface(x, y):
    a = [x, y]
    global line_select
    global state
    for index, value in enumerate(list_matchstick):
        z = value.pos()
        if (abs(a[0] - z[0]) < 10 and abs(a[1] - z[1]) < 25) and (
                line_select.get() == -1 or z[1] == line_select.get()):
            value.ht()
            state -= 1
            win()
            if line_select.get() == -1:
                line_select.set(z[1])


# La variable état représente le nombre d'allumettes restantes en jeu, quand elle est à 0,
# l'avant-dernier joueur est le gagnant.

def win():
    if state == 0:
        window_toto2 = Toplevel(window_toto)
        announce = Label(window_toto2, text=f"Congratulations Player {state_player.get()}, "
                                            f"you've won !!!")
        announce.pack()
        ok_btn = Button(window_toto2, text="OK", command=window_toto2.destroy)
        ok_btn.pack()

        pos_x = window_toto2.winfo_screenwidth()
        pos_y = window_toto2.winfo_screenheight()
        diff_x = 300
        diff_y = 50
        x = (pos_x / 2) - (diff_x / 2)
        y = (pos_y / 2) - (diff_y / 2)
        window_toto2.geometry('%dx%d+%d+%d' % (diff_x, diff_y, x, y))


# Fonction qui réinitialise les variables afin de pouvoir faire une nouvelle partie
def new_part():
    global state, state_player, line_select, list_matchstick
    state = 16
    state_player.set(2)
    line_select.set(-1)
    for match in list_matchstick:
        match.st()


# Création d'une fenêtre TK pour pouvoir y placer les boutons radio, ainsi que le bouton recommencer

window_toto = Tk()
window_toto.title("Matchstick")

posx = window_toto.winfo_screenwidth()
posy = window_toto.winfo_screenheight()
# Dimension de la fenêtre 800x600
diffx = 800
diffy = 600
x0 = (posx / 2) - (diffx / 2)
y0 = (posy / 2) - (diffy / 2)
window_toto.geometry('%dx%d+%d+%d' % (diffx, diffy, x0, y0))

canvas1 = Canvas(window_toto, width=800, height=600)
canvas1.pack()
screen1 = TurtleScreen(canvas1)
state_player = IntVar()
line_select = IntVar()

# Création des 16 curseurs qui auront l'image d'une allumette
# On les place dans une liste afin de faciliter leur gestion (leur assigner l'image de l'allumette,
# les placer au bon endroit etc
list_matchstick = [RawTurtle(screen1) for _ in range(16)]

screen1.register_shape("Allumettes/allumettes.gif")
screen1.bgpic("Allumettes/alu2.gif")

for i in list_matchstick:
    i.shape("Allumettes/allumettes.gif")

# Cette liste contient les positions de chaque allumette, afin qu'elles représentent un triangle
triangle_toto = [[0, 210], [-30, 140], [0, 140], [30, 140], [-60, 70], [-30, 70], [0, 70], [30, 70],
                 [60, 70], [-90, 0], [-60, 0], [-30, 0], [0, 0], [30, 0], [60, 0], [90, 0]]

# On place les allumettes correctement
for index, value in enumerate(triangle_toto):
    list_matchstick[index].up()
    list_matchstick[index].goto(value)
    list_matchstick[index].down()

new_part()

for i in list_matchstick:
    i.onclick(efface, btn=1)

# Création des 2 boutons radio pour changer de joueur et du bouton recommencer
player_1 = Radiobutton(text="Joueur 1", variable=state_player, value=2,
                       command=lambda: [line_select.set(-1)])
player_2 = Radiobutton(text="Joueur 2", variable=state_player, value=1,
                       command=lambda: [line_select.set(-1)])
reco = Button(text="Nouvelle Partie", command=new_part)

# On les place correctement
player_1.place(x=150, y=100)
player_2.place(x=150, y=150)
reco.place(x=150, y=200)

window_toto.mainloop()
