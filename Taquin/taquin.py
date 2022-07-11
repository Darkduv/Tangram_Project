#! /usr/bin/python
# -*- coding: utf-8 -*-

"""'Taquin' Game"""

import tkinter
from random import randrange


def shuffle_and_init(position_, bouton_, nb_shuffle=1000):
    """Cette fonction mélange le taquin"""
    for _ in range(nb_shuffle):

        vide = position_[15]
        # on récupère la position de la case vide
        perm = [(vide[0] + 200, vide[1]), (vide[0], vide[1] - 200),
                (vide[0] - 200, vide[1]), (vide[0], vide[1] + 200),
                (vide[0] + 200, vide[1]), (vide[0], vide[1] - 200),
                (vide[0] - 200, vide[1]), (vide[0], vide[1] + 200),
                (vide[0] + 200, vide[1]), (vide[0], vide[1] - 200),
                (vide[0] - 200, vide[1]), (vide[0], vide[1] + 200)]
        # perm contient les positions où la case vide va pouvoir aller.
        # Chaque position y est plusieurs fois pour augmenter l'impression de
        # hasard de randrange
        count = len(perm)
        jj = randrange(0, count - 1)

        while perm[jj] not in position_:
            jj = randrange(0, count - 1)
            # on tire une position au hasard jusqu'à en avoir une où on peut
            # mettre la case vide
            # (il ne faut pas que cela soit en dehors de l'écran)

        current = perm[jj]
        # on récupère la future position de la case vide
        btn = bouton_[position_.index(current)]
        # on regarde quel morceau de l'image est à cette position
        btn.place(x=vide[0], y=vide[1])
        # on met cette image à la place de la case vide
        position_[15] = current
        position_[bouton_.index(btn)] = vide
        # on met à jour la table des positions


def depl(btn, position_, bouton_):
    """Cette fonction déplace une image"""
    vide = position_[15]
    # on récupère la position de la case vide
    current = position_[bouton_.index(btn)]
    # on récupère la position de la case sur laquelle on a cliqué
    if (abs(current[0] - vide[0]) <= 5 and abs(current[1] - vide[1]) <= 210) \
            or (abs(current[1] - vide[1]) <= 5
                and abs(current[0] - vide[0]) <= 210):
        # si les deux cases sont voisines :
        btn.place(x=vide[0], y=vide[1])
        # on met la case à la place de la case vide
        position[15] = current
        # on met à jour la table des positions
        position[bouton_.index(btn)] = vide


def detec(_):
    """Cette fonction détecte si le joueur a gagné"""
    global position, tab_end, main_window, bouton

    if position == tab_end:
        # if the current positions are the same as the positions of the
        # finished Taquin :
        fenetre_fin = tkinter.Toplevel(main_window)
        gagne = tkinter.Label(fenetre_fin,
                              text="Félicitations vous avez réussi !")
        btngagne = tkinter.Button(fenetre_fin, text="OK",
                                  command=fenetre_fin.destroy)
        bouton[15].place(x=0, y=0)
        # create a window to notify the player and display the uncut image
        posx_ = fenetre_fin.winfo_screenwidth()
        posy_ = fenetre_fin.winfo_screenheight()
        diffx_ = 200
        diffy_ = 50
        x_ = (posx_ / 2) - (diffx_ / 2)
        y_ = (posy_ / 2) - (diffy_ / 2)
        fenetre_fin.geometry('%dx%d+%d+%d' % (diffx_, diffy_, x_, y_))
        # on centre la fenêtre

        gagne.pack()
        btngagne.pack()
        # on affiche la fenêtre de notification et son contenu


# fenêtre principale
main_window = tkinter.Tk()
main_window.title("Taquin Project")


def init_position_and_tab_end():
    """Give the table to initialise `tab_end` and `position`"""
    return [(0.00, 0.00), (200.00, 0.00), (400.00, 0.00), (600.00, 0.00),
            (0.00, 200.00), (200.00, 200.00), (400.00, 200.00),
            (600.00, 200.00), (0.00, 400.00), (200.00, 400.00),
            (400.00, 400.00), (600.00, 400.00), (0.00, 600.00),
            (200.00, 600.00), (400.00, 600.00), (600.00, 600.00)]


tab_end = init_position_and_tab_end()
# Création de la table de position finie

posx = main_window.winfo_screenwidth()
posy = main_window.winfo_screenheight()
diffx = 800
diffy = 800
x = (posx / 2) - (diffx / 2)
y = (posy / 2) - (diffy / 2)
main_window.geometry('%dx%d+%d+%d' % (diffx, diffy, x, y))
# on centre la fenêtre

case1 = tkinter.PhotoImage(file="Taquin/1.gif")
case2 = tkinter.PhotoImage(file="Taquin/2.gif")
case3 = tkinter.PhotoImage(file="Taquin/3.gif")
case4 = tkinter.PhotoImage(file="Taquin/4.gif")
case5 = tkinter.PhotoImage(file="Taquin/5.gif")
case6 = tkinter.PhotoImage(file="Taquin/6.gif")
case7 = tkinter.PhotoImage(file="Taquin/7.gif")
case8 = tkinter.PhotoImage(file="Taquin/8.gif")
case9 = tkinter.PhotoImage(file="Taquin/9.gif")
case10 = tkinter.PhotoImage(file="Taquin/10.gif")
case11 = tkinter.PhotoImage(file="Taquin/11.gif")
case12 = tkinter.PhotoImage(file="Taquin/12.gif")
case13 = tkinter.PhotoImage(file="Taquin/13.gif")
case14 = tkinter.PhotoImage(file="Taquin/14.gif")
case15 = tkinter.PhotoImage(file="Taquin/15.gif")
taquin = tkinter.PhotoImage(file="Taquin/Taquin.gif")
# on importe les images du Taquin
# (le jeu devant être lancé depuis le Tangram on lui indique le dossier
# à partir du dossier contenant main.py)

img0 = tkinter.Button(
    text="0", command=lambda: depl(img0, position, bouton), image=case1)
img1 = tkinter.Button(
    text="1", command=lambda: depl(img1, position, bouton), image=case2)
img2 = tkinter.Button(
    text="2", command=lambda: depl(img2, position, bouton), image=case3)
img3 = tkinter.Button(
    text="3", command=lambda: depl(img3, position, bouton), image=case4)
img4 = tkinter.Button(
    text="4", command=lambda: depl(img4, position, bouton), image=case5)
img5 = tkinter.Button(
    text="5", command=lambda: depl(img5, position, bouton), image=case6)
img6 = tkinter.Button(
    text="6", command=lambda: depl(img6, position, bouton), image=case7)
img7 = tkinter.Button(
    text="7", command=lambda: depl(img7, position, bouton), image=case8)
img8 = tkinter.Button(
    text="8", command=lambda: depl(img8, position, bouton), image=case9)
img9 = tkinter.Button(
    text="9", command=lambda: depl(img9, position, bouton), image=case10)
img10 = tkinter.Button(
    text="10", command=lambda: depl(img10, position, bouton), image=case11)
img11 = tkinter.Button(
    text="11", command=lambda: depl(img11, position, bouton), image=case12)
img12 = tkinter.Button(
    text="12", command=lambda: depl(img12, position, bouton), image=case13)
img13 = tkinter.Button(
    text="13", command=lambda: depl(img13, position, bouton), image=case14)
img14 = tkinter.Button(
    text="14", command=lambda: depl(img14, position, bouton), image=case15)
img15 = tkinter.Label(main_window, image=taquin)
# on crée des boutons contenant les images et qui lancent la fonction depl
# sur eux-même (grâce à 'lambda') lorsque l'on clique dessus. img15 représente
# la case vide et aussi l'image complète que l'on affiche si le jeu est fini

# Ce tableau contient le nom des boutons dans l'ordre
bouton = [img0, img1, img2, img3, img4, img5, img6, img7, img8, img9, img10,
          img11, img12, img13, img14, img15]
# Ce tableau contient les positions des boutons, son index correspond
# à celui du tableau bouton
position = init_position_and_tab_end()

# on mélange la liste et on affiche les cases
for i, j in enumerate(tab_end):
    if i < 15:
        # on fait attention de bien garder la correspondance
        # d'indexage entre position et bouton
        bouton[i].place(x=j[0], y=j[1])
        position[i] = j
    else:
        # on ne veut pas afficher img15 qui ne doit l'être
        # que quand le Taquin est fini
        position[i] = j

shuffle_and_init(position, bouton)
# on mélange le Taquin quand tout est prêt

main_window.bind("<tkinter.ButtonRelease-1>", detec)
# lorsque l'on relâche le clic droit, on lance la détection.

main_window.mainloop()
# boucle principale
