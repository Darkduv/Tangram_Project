# ! /usr/bin/python
# -*- coding: utf-8 -*-

"""Tangram Game. See Readme.md for more"""


import turtle
import tkinter
from random import randrange
import os
import pickle

# Fonctions
from math import sqrt

from typing import Union, Any, Optional
from dataclasses import dataclass


def distance(p1: tuple[Any, Any], p2: tuple[Any, Any]) -> float:
    """Computes the distance between two points p1, p2"""
    dist = sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))
    return dist


def window_geometry(window: Union[tkinter.Tk, tkinter.Toplevel], width: int,
                    height: int) -> None:
    """Set geometry of the window _fen"""
    pos_x_, pos_y_ = window.winfo_screenwidth(), window.winfo_screenheight()
    x_ = int((pos_x_ / 2) - (width / 2))
    y_ = int((pos_y_ / 2) - (height / 2))
    window.geometry(f'{width}x{height}+{x_}+{y_}')


def sav_color(l_color) -> None:
    """Retrieves and saves in a file the colors chosen by the player"""
    with open("sav_color.txt", "wb") as sauvegarde_couleur:
        sav = pickle.Pickler(sauvegarde_couleur)
        for col in l_color:
            sav.dump(col.get())


def sav_resolution(resolution: str) -> None:
    """Change la résolution par défaut par celle sélectionnée par le joueur
     et la place dans le fichier qui est lu au démarrage du jeu
      pour initialiser les fenêtres"""
    with open("sav_res.txt", "wb") as saved_resolution_file:
        sav = pickle.Pickler(saved_resolution_file)
        sav.dump(resolution)

    # création et centrage d'une fenêtre demandant au joueur de redémarrer
    #  l'application pour que les changements prennent effet
    advise = tkinter.Toplevel()
    redem = tkinter.Label(advise,
                          text="Vous devez relancer l'application"
                               " pour que les changements prennent effet !")
    btn_quit = tkinter.Button(advise, text="Fermer l'application",
                              command=fen.quit)
    redem.pack()
    btn_quit.pack()

    window_geometry(advise, 500, 50)


name_pieces = ['tri1', 'tri2', 'tri_moy', 'tripe1', 'tripe2', 'carre', 'para']
l_seuil_rotation = [24, 24, 24, 24, 24, 6, 12]
d_seuil_rotation = {'tri1': 24, 'tri2': 24, 'tri_moy': 24, 'tripe1': 24,
                    'tripe2': 24, 'carre': 24, 'para': 24}


class Piece(turtle.RawTurtle):
    """Piece of tangram"""

    def __init__(self, name: str, screen: turtle.Screen, modulo_rot: int):
        super().__init__(screen)
        self.name = name
        self.screen = screen
        self.rot = 0
        self.modulo_rot = modulo_rot
        # self.onclick(lambda x, y: print(self.name))
        self.onclick(self.rotation, btn=3)
        self.onclick(lambda x, y: print(self.name), btn=1)

        self.ondrag(self.goto)

    def rotation(self, *_) -> None:
        self.rot += 1
        self.rot %= self.modulo_rot
        self.seth(self.rot * 15)
        self.screen.update()

# FIXME : changer la structure, on veut stocker la liste des configurations
#  des pièces: position et rotation doivent être liés ensemble, pièce par pièce

# Fixme bis: stockage des pièces ? liste/dict[nom] ?


@dataclass
class TangramShape:
    """Describes a tangram shape : positions of the pieces, rotation, etc."""

    name: str
    positions: list[tuple[float, float]]
    rotations: list[int]
    para_flipped: bool
    img_file: Optional[str]


class Tangram:
    """Tangram main window/game"""

    # Création des premières variables : les couleurs, les couleurs par défaut

    _color_default = ("brown", "purple", "pink", "yellow",
                      "blue", "red", "green")

    _liste_init_color = [["Rouge", "red"], ["Bleu", "blue"],
                         ["Vert", "green"], ["Jaune", "yellow"],
                         ["Rose", "pink"], ["Violet", "purple"],
                         ["Noir", "black"], ["Blanc", "white"],
                         ["Orange", "orange"], ["Bleu Ciel", "skyblue"],
                         ["Or", "gold"], ["Marron", "brown"]]

    def __init__(self):
        """Main class for the tangram game"""

        self.hints = 2
        self.flipped = False

        # Initialisation de la résolution
        # lecture dans sav_res.txt de la résolution du programme
        # (par défaut 1000x700)
        with open("sav_res.txt", "rb") as saved_resolution_:
            res_val_ = pickle.Unpickler(saved_resolution_)
            self.res = res_val_.load()

        fen2 = tkinter.Toplevel()
        # Création d'une nouvelle fenêtre
        cv1 = tkinter.Canvas(fen2, width=CONFIG_RES[self.res]["window"][0],
                             height=CONFIG_RES[self.res]["window"][1])
        self.s1 = turtle.TurtleScreen(cv1)
        # Création d'un canvas Tkinter dans lequel on crée un écran turtle

        self.dict_piece = {name: Piece(name, self.s1, d_seuil_rotation[name])
                           for name in name_pieces}
        # création des curseurs qui seront les éléments du Tangram

        # affichage du canvas(et donc de l'écran turtle)
        cv1.pack()
        # création des objets qui contiendront les couleurs des curseurs,
        # On utilise ici des objets pour permettre la mise à jour simple
        # des couleurs grâce à des boutons radio
        self.l_color = self.load_color()

        # We will now create the menu that is located at
        # the top of the game window
        menu1 = tkinter.Menu(fen2)

        fichier = tkinter.Menu(menu1, tearoff=0)
        menu1.add_cascade(label="Fichier", menu=fichier)
        fichier.add_command(label="Recommencer", command=self.restart)
        # la commande Fichier/recommencer permet au joueur
        # de remettre son niveau
        # à 0 grâce à la fonction restart
        options = tkinter.Menu(fichier, tearoff=0)
        fichier.add_cascade(label="Options", menu=options)
        color = tkinter.Menu(options, tearoff=1)
        options.add_cascade(label="Couleur", menu=color)
        list_menus = [tkinter.Menu(options, tearoff=0) for _ in range(7)]
        # ici nous allons définir un menu pour chaque élément du tangram qui
        # permettra au joueur de personnaliser les couleurs de son jeu qui sont
        # automatiquement mises à jour grâce à la fonction color_init()

        liste_init = [["Triangle 1", list_menus[0], self.l_color[0]],
                      ["Triangle 2", list_menus[1], self.l_color[1]],
                      ["Triangle Moyen", list_menus[2], self.l_color[2]],
                      ["Petit Triangle 1", list_menus[3], self.l_color[3]],
                      ["Petit Triangle 2", list_menus[4], self.l_color[4]],
                      ["Carre", list_menus[5], self.l_color[5]],
                      ["Parallélogramme", list_menus[6], self.l_color[6]]]

        for i_label, i_menu, i_color in liste_init:
            color.add_cascade(label=i_label, menu=i_menu)
            for j_label, j_val in self._liste_init_color:
                i_menu.add_radiobutton(label=j_label, value=j_val,
                                       variable=i_color,
                                       command=self.color_init)

        color.add_separator()

        color.add_command(label="Défaut", command=self.apply_color_default)
        # permet au joueur de remettre les couleurs par défaut du jeu
        color.add_separator()
        color.add_command(label="Sauvegarder", command=sav_color)
        # sauvegarde la configuration des couleurs grâce à la fonction
        resolution = tkinter.Menu(options, tearoff=0)
        options.add_cascade(label="Résolution", menu=resolution)
        resolution.add_command(label="1000x700",
                               command=lambda: sav_resolution("1000x700"))
        resolution.add_command(label="500x350",
                               command=lambda: sav_resolution("500x350"))
        # permet de modifier la résolution courante
        fichier.add_command(label="Quitter", command=fen.quit)
        # permet au joueur de quitter complètement le programme

        niveaux = tkinter.Menu(menu1, tearoff=0)
        menu1.add_cascade(label="Niveau", menu=niveaux)

        dict_levels = {"Canard": CANARD, "Lapin": LAPIN,
                       "Homme prosterné": PROSTERNE, "Homme rigolant": FIGURE}

        def create_command(lvl_shape: TangramShape):
            def command():
                self.apply_level(lvl_shape)
            return command

        for label, shape in dict_levels.items():
            niveaux.add_command(label=label, command=create_command(shape))
        # permet de choisir le niveau

        aide = tkinter.Menu(menu1, tearoff=0)
        menu1.add_cascade(label="Aide", menu=aide)

        aide.add_command(label=f"Coups de pouce : {self.hints} par partie",
                         command=self.hint)
        # lance la fonction hint pour placer un des éléments du Tangram
        aide.add_command(label="Comment Jouer ?",
                         command=lambda: os.system("gedit comment_jouer.txt"))
        # affiche dans gedit le fichier comment_jouer.txt

        bonus = tkinter.Menu(menu1, tearoff=0)
        menu1.add_cascade(label="Bonus", menu=bonus)
        bonus.add_command(label="Taquin",
                          command=lambda: os.system("python Taquin/taquin.py"))
        bonus.add_command(label="Allumettes",
                          command=lambda: os.system(
                              "python Allumettes/allumettes.py"))
        # permet de lancer les scripts contenant les jeux bonus :
        # le jeu d'Allumette et le Taquin

        fen2.config(menu=menu1)
        # affectation du menu à notre fenêtre de jeu

        window_geometry(fen2, *CONFIG_RES[self.res]["window"])
        # centrage de la fenêtre de jeu

        self.s1.tracer(8, 25)
        # configure la vitesse de tracé du curseur p
        # de façon à ce que l'on ne remarque pas l'initialisation des curseurs

        def tri_pe(demi_hyp):
            def aux(tortue):
                tortue.fd(demi_hyp)
                tortue.right(135)
                tortue.fd(demi_hyp * sqrt(2))
                tortue.right(90)
                tortue.fd(demi_hyp * sqrt(2))
                tortue.seth(0)
                tortue.fd(demi_hyp)
                tortue.end_poly()

            return aux

        def tri_moy_(tortue):
            cote_ = CONFIG_RES[self.res]["cote"]
            tortue.left(45)
            tortue.fd(sqrt((cote_ / 2) ** 2 + (cote_ / 2) ** 2) / 2)
            tortue.right(135)
            tortue.fd(cote_ / 2)
            tortue.right(90)
            tortue.fd(cote_ / 2)
            tortue.goto(0, 0)

        self.register_shape_init(tri_pe(CONFIG_RES[self.res]["cote"] / 2),
                                 ['tri1', 'tri2'])
        self.register_shape_init(tri_pe(CONFIG_RES[self.res]["cote"] / 4),
                                 ['tripe1', 'tripe2'])

        def parallelo_both(reverse_: bool = False):
            cote_ = CONFIG_RES[self.res]["cote"]

            def parallelo(tortue):
                dist = sqrt(2) * cote_ / 4
                tortue.left(-90 if reverse_ else 90)
                tortue.fd(dist / 2)
                tortue.right(-90 if reverse_ else 90)
                tortue.fd(cote_ / 8)
                tortue.right(90)
                tortue.fd(cote_ / 4)
                tortue.seth(135 if reverse_ else 225)
                tortue.fd(dist)
                tortue.seth(90)
                tortue.fd(cote_ / 2)
                tortue.seth(315 if reverse_ else 45)
                tortue.fd(dist)
                tortue.seth(0 if reverse_ else 270)
                if reverse_:
                    tortue.right(90)
                tortue.fd(cote_ / 4)
                tortue.right(90)
                tortue.fd(cote_ / 8)
                tortue.goto(0, 0)
                if not reverse_:
                    tortue.seth(0)

            return parallelo

        self.register_shape_init(parallelo_both(), ['para1'])
        self.register_shape_init(parallelo_both(reverse_=True), ['para2'])

        def carre_(tortue):
            cote_ = CONFIG_RES[self.res]["cote"]
            demi_size = sqrt((cote_ / 2) ** 2 + (cote_ / 2) ** 2) / 4
            tortue.left(90)

            for trace in range(6):
                tortue.fd(demi_size if trace in [0, 1, 5] else demi_size * 2)
                tortue.right(90)

            tortue.fd(demi_size)
            tortue.seth(0)

        self.register_shape_init(carre_, ['carre'])
        self.register_shape_init(tri_moy_, ['tri_moy'])

        # Corps
        self.lvl = CANARD
        self.apply_level(CANARD)

        cv1.bind("<ButtonRelease-1>", self.check_end)
        cv1.bind("<Double-Button-1>", self.flip_para)

        # et pour permettre au joueur de faire le symétrique du parallélogramme

        self.s1.listen()
        # il ne reste plus qu'à attendre un évènement

    @staticmethod
    def load_color() -> list[tkinter.StringVar]:
        l_color = []
        for i in range(7):
            l_color.append(tkinter.StringVar())
        with open("sav_color.txt", "rb") as saved_colors:
            color_val = pickle.Unpickler(saved_colors)
            for i in range(7):
                # read the colors saved by the player in the file sav_color.txt
                color = color_val.load()
                # assigning strings containing color names
                l_color[i].set(color)
        return l_color

    def hint(self) -> None:
        """Allows the player to get help if the player requests it"""

        if self.hints >= 1:
            # si le joueur a droit à un peu d'aide, on l'aide
            curseur = [self.dict_piece[name] for name in name_pieces]

            cpt = len(curseur)
            j = randrange(0, cpt)
            # on tire un curseur au hasard

            figure = self.lvl
            curseur[j].goto(figure.positions[j])
            curseur[j].seth(figure.rotations[j] * 15)

            if self.flipped != figure.para_flipped \
                    and (
                    curseur[j].shape() == "para1"
                    or curseur[j].shape() == "para2"):
                self.flip_para()
            # for the current level, we put the randomly drawn cursor
            # in its place, rotate it correctly and update the table
            # of positions and rotations. If the cursor drawn is
            # dict_piece['para'], we also check whether it should be returned,
            # and we run the flip_para function which updates reverse

            self.hints -= 1
            # on décrémente helped car l'aide est limitée par jeu
        else:
            # If the player has used the help too many times, he/she is told
            # in a window that he/she can no longer use this function
            # for the time being.
            self.no_more_hint()

        self.s1.update()

    @staticmethod
    def no_more_hint() -> None:
        fen4 = tkinter.Toplevel()
        attention = tkinter.Label(
            fen4, text="Attention vous avez utilisé l'aide trop de fois ! ")
        btn_ok = tkinter.Button(fen4, text="OK", command=fen4.destroy)
        attention.pack()
        btn_ok.pack()

        window_geometry(fen4, 300, 50)

    def restart(self) -> None:
        """Restarts the current level"""

        # récupération des variables à modifier en tant que variable globale

        init_figure = CARRE
        self.flipped = init_figure.para_flipped
        # the variable `helped` is reset to 2 (see function `hint()`)
        self.hints = 2
        # call of the function init for the changes to take effect.

        for i, name in enumerate(name_pieces):
            self.dict_piece[name].up()

            self.dict_piece[name].shape(name if name != 'para' else 'para1')

            self.dict_piece[name].seth(init_figure.rotations[i] * 15)
            self.dict_piece[name].rot = init_figure.rotations[i]
            self.dict_piece[name].goto(init_figure.positions[i])

        # self.s1.update()
        self.color_init()

    def color_init(self) -> None:
        """Update the color of the elements of the tangram.

        (allows the player to customise the game)"""
        for i, name in enumerate(name_pieces):
            self.dict_piece[name].color(self.l_color[i].get())

        self.s1.update()

    def apply_color_default(self) -> None:
        for col, default_col in zip(self.l_color, self._color_default):
            col.set(default_col)
        self.color_init()

    def apply_level(self, lvl: TangramShape) -> None:
        """Configures the game to display the level chosen by the user"""
        self.lvl = lvl

        bgc = lvl.img_file
        self.s1.bgpic(bgc)

        self.restart()

    def end_tangram_level(self) -> None:
        fen3 = tkinter.Toplevel()  # Initialisation d'une fenêtre
        # qui a un fond que l'on affiche grâce à un label
        fen3.title("Bravo !")
        fond = tkinter.Label(fen3, image=image6)  # le fond est ici une image

        # Creation of a restart and quit button.
        # (the 'quit' one quit everything)
        restart = tkinter.Button(
            fond, image=image7,
            command=lambda: [self.restart(), fen3.destroy()])
        by = tkinter.Button(fond, image=image8, command=fen.quit)

        fond.pack()
        # affichage et centrage de la fenêtre.
        restart.place(x=CONFIG_RES[self.res]["x_res"],
                      y=CONFIG_RES[self.res]["y_res"])
        by.place(x=CONFIG_RES[self.res]["xby"],
                 y=CONFIG_RES[self.res]["yby"])
        window_geometry(fen3, *CONFIG_RES[self.res]["end_window"])

    def pos_pieces(self) -> list[tuple[float, float]]:
        l_pos = []
        for name in name_pieces:
            piece = self.dict_piece[name]  # type: Piece
            l_pos.append(piece.position())
        return l_pos

    def check_end(self, _) -> bool:
        """Cette fonction détecte si le niveau est terminé ou non"""
        dist_lim = 5
        # if a piece is in position with dist < dist_lim,
        # we place it automatically
        pos_pieces = self.pos_pieces()
        for i, pt in enumerate(self.lvl.positions):

            # Firstly: checks the positions
            # the two big triangles
            if i in [0, 1]:
                if distance(pos_pieces[i], pt) > dist_lim \
                        and distance(pos_pieces[1 - i], pt) > dist_lim:
                    return False
                d1 = distance(pos_pieces[0], pt)
                d2 = distance(pos_pieces[1], pt)
                if d1 < d2:
                    self.dict_piece['tri1'].goto(self.lvl.positions[i])
                elif d1 - d2 < 5:
                    self.dict_piece['tri1'].goto(self.lvl.positions[i])
                    self.dict_piece['tri2'].goto(self.lvl.positions[i])
                else:
                    self.dict_piece['tri2'].goto(self.lvl.positions[i])

            # the two small triangles
            if i in [3, 4]:
                if distance(pos_pieces[i], pt) > dist_lim \
                        and distance(pos_pieces[7 - i], pt) > dist_lim:
                    return False
                d1 = distance(pos_pieces[3], pt)
                d2 = distance(pos_pieces[4], pt)
                if d1 < d2:
                    self.dict_piece['tripe1'].goto(self.lvl.positions[i])
                elif d1 - d2 < 5:
                    self.dict_piece['tripe1'].goto(self.lvl.positions[i])
                    self.dict_piece['tripe2'].goto(self.lvl.positions[i])
                else:
                    self.dict_piece['tripe2'].goto(self.lvl.positions[i])

            # These first 4 tests were more complex, because we don't know
            # which triangle the player will use (2 places for each triangle)

            # the middle triangle, the square, the parallelogram
            if i in [2, 5, 6]:
                if distance(pos_pieces[i], pt) > dist_lim:
                    return False
                self.dict_piece[name_pieces[i]].goto(pt)

        # second test: check if the rotation is the right one.
        for i, name in enumerate(name_pieces):
            cpt = self.dict_piece[name].rot
            if i in [0, 1]:
                if cpt not in [self.lvl.rotations[0], self.lvl.rotations[1]]:
                    return False
            elif i in [3, 4]:
                if cpt not in [self.lvl.rotations[3], self.lvl.rotations[4]]:
                    return False
            elif i in [2, 5, 6]:
                if cpt != self.lvl.rotations[i]:
                    return False

        # Last test checking if the parallelogram must be reversed or not.
        if self.flipped != self.lvl.para_flipped:
            return False

        self.s1.update()

        self.end_tangram_level()
        return True

    def flip_para(self, *_) -> None:
        """Récupère la forme de l'objet C_para et lui assigne sa forme
         symétrique"""

        forme = self.dict_piece['para'].shape()
        if forme == "para1":
            self.flipped = True
            self.dict_piece['para'].shape("para2")
        if forme == "para2":
            self.flipped = False
            self.dict_piece['para'].shape("para1")
        self.s1.update()

    # pour créer les curseurs on enregistre une forme que l'on
    # dessine avec le curseur p puis on l'enregistre en tant
    # que shape pour notre écran turtle
    def register_shape_init(self, dessine_forme, l_name_shape) -> None:
        """Enregistre le polygone formé par dessine_forme"""
        my_turtle = turtle.RawTurtle(self.s1)
        my_turtle.ht()
        my_turtle.up()
        my_turtle.begin_poly()
        dessine_forme(my_turtle)
        shape_ = my_turtle.get_poly()
        for name in l_name_shape:
            self.s1.register_shape(name, shape_)


with open("sav_res.txt", "rb") as saved_resolution:
    res_val = pickle.Unpickler(saved_resolution)
    res = res_val.load()
# Première fenêtre

fen = tkinter.Tk()
fen.title("Tangram Project")


# importation des images qui dépendent de la résolution (le fond des fenêtres)
image1 = tkinter.PhotoImage(file=f"HT/{res}/Tangram.gif")
image2 = tkinter.PhotoImage(file=f"HT/{res}/main.gif")
image3 = tkinter.PhotoImage(file=f"HT/{res}/Jouer.gif")
image4 = tkinter.PhotoImage(file=f"HT/{res}/Crédits.gif")
image5 = tkinter.PhotoImage(file=f"HT/{res}/Quitter.gif")
image6 = tkinter.PhotoImage(file=f"HT/{res}/end.gif")
image7 = tkinter.PhotoImage(file=f"HT/{res}/reco.gif")
image8 = tkinter.PhotoImage(file=f"HT/{res}/quitter_end.gif")

# configuration de la taille des fenêtres principales
# et de la fenêtre de fin de jeu
CONFIG_RES = {
    "1000x700": {
        "window": (1000, 700),
        "end_window": (300, 210),
        "cote": 200,  # taille du côté principal des éléments du tangram
        # configuration des emplacements des différents boutons
        # qui dépendent de la résolution contenue dans les fenêtres
        "x_btn": 410, "y_btn": 252, "x_btn1": 400, "y_btn1": 375, "x_btn2": 400,
        "y_btn2": 490,
        "x_res": 5, "y_res": 140, "xby": 180, "yby": 137
    },
    "500x350": {
        "window": (500, 350),
        "end_window": (150, 105),
        "cote": 100,
        "x_btn": 205, "y_btn": 126, "x_btn1": 200, "y_btn1": 188, "x_btn2": 200,
        "y_btn2": 245,
        "x_res": 3, "y_res": 70, "xby": 90, "yby": 69
    }
}
position_res = {
    '1000x700': {
        'CARRE': [(409.00, 2.00), (308.00, -99.00), (257.00, 52.00),
                  (358.00, 103.00),
                  (258.00, 1.00), (308.00, 53.00), (232.00, -34.00)],
        'CANARD': [(-161.00, -21.00), (-160.00, -21.00), (-262.00, -91.00),
                   (-384.00, 10.00),
                   (-60.00, 30.00), (-334.00, 61.00), (-309.00, -25.00)],
        'PROSTERNE': [(-230.00, 26.00), (-154.00, 18.00), (-292.00, -21.00),
                      (-304.00, 28.00),
                      (-86.00, -107.00), (-39.00, -25.00), (-319.00, -55.00)],
        'LAPIN': [(-281.00, -115.00), (-251.00, -44.00), (-253.00, 128.00),
                  (-200.00, -81.00),
                  (-250.00, -30.00), (-216.00, 59.00), (-198.00, 137.00)],
        'FIGURE': [(-223.00, 16.00), (-240.00, -111.00), (-228.00, 138.00),
                   (-285.00, 26.00),
                   (-322.00, 33.00), (-219.00, -39.00), (-184.00, 131.00)]
    },
    '500x350': {
        'CARRE': [(204.5, 1.0), (154.0, -49.5), (128.5, 26.0), (179.0, 51.5),
                  (129.0, 0.5),
                  (154.0, 26.5), (116.0, -17.0)],
        'CANARD': [(-80.5, -10.5), (-80.0, -10.5), (-131.0, -45.5),
                   (-192.0, 5.0), (-30.0, 15.0),
                   (-167.0, 30.5), (-154.5, -12.5)],
        'PROSTERNE': [(-115.0, 13.0), (-77.0, 9.0), (-146.0, -10.5),
                      (-152.0, 14.0), (-43.0, -53.5),
                      (-19.5, -12.5), (-159.5, -27.5)],
        'LAPIN': [(-140.5, -57.5), (-125.5, -22.0), (-126.5, 64.0),
                  (-100.0, -40.5),
                  (-125.0, -15.0), (-108.0, 29.5), (-99.0, 68.5)],
        'FIGURE': [(-111.5, 8.0), (-120.0, -55.5), (-114.0, 69.0),
                   (-142.5, 13.0), (-161.0, 16.5),
                   (-109.5, -19.5), (-92.0, 65.5)]
    }
}
# tableaux contenant toutes les informations pour la réalisation des niveaux
# ( 1: emplacement, 2: rotation, 3: `reverse` value,
#  4: emplacement de l'image de fond associée)
CARRE = TangramShape('CARRE', position_res[res]['CARRE'],
                     [0, 18, 18, 6, 12, 3, 6], False, None)
CANARD = TangramShape('CANARD', position_res[res]['CANARD'],
                      [0, 12, 15, 12, 6, 3, 6], False, f"HT/{res}/canard.gif")
PROSTERNE = TangramShape('PROSTERNE', position_res[res]['PROSTERNE'],
                         [16, 13, 13, 19, 16, 2, 1], False,
                         f"HT/{res}/prosterne.gif")
LAPIN = TangramShape('LAPIN', position_res[res]['LAPIN'],
                     [3, 0, 21, 0, 12, 0, 4], False, f"HT/{res}/lapin.gif")
FIGURE = TangramShape('FIGURE', position_res[res]['FIGURE'],
                      [15, 9, 0, 12, 9, 3, 9], True, f"HT/{res}/figure.gif")

if res not in ["1000x700", '500x350']:
    raise ValueError("Seules les résolutions 1000x700 ou 500x350 sont prévues.")

# Fin de l'initialisation de la fenêtre

lab0 = tkinter.Label(fen, image=image1)
# Ce label contient l'image de fond (la première de l'animation)
btn = tkinter.Button(lab0, text="Jouer",
                     command=Tangram, image=image3)
btn1 = tkinter.Button(lab0, text="Crédits",
                      command=lambda: os.system("gedit Crédits.txt"),
                      image=image4)
btn2 = tkinter.Button(lab0, text="Quitter", command=fen.quit, image=image5)
# Création de 3 boutons permettant de jouer au tangram,
# de quitter le jeu ou d'afficher dans gedit le fichier crédits.txt

# récupération de la position de la fenêtre (ne marche que sous linux (?))
window_geometry(fen, *CONFIG_RES[res]["window"])
# centrage de la fenêtre

lab0.pack(side='top', fill='both', expand=1)
# affichage du fond

fen.after(2500, lambda: [lab0.configure(image=image2),
                         btn.place(x=CONFIG_RES[res]["x_btn"],
                                   y=CONFIG_RES[res]["y_btn"]),
                         btn1.place(x=CONFIG_RES[res]["x_btn1"],
                                    y=CONFIG_RES[res]["y_btn1"]),
                         btn2.place(x=CONFIG_RES[res]["x_btn2"],
                                    y=CONFIG_RES[res]["y_btn2"])]
          )
# après 2,5 secondes, on change l'image de fond et on affiche les boutons
#  configurés plus haut, cette ligne permet de créer l'animation du début


# on entre dans la boucle principale...
fen.mainloop()
# ... et on détruit la fenêtre principale si l'on en sort.
fen.destroy()
