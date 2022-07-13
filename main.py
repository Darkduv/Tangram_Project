# ! /usr/bin/python
# -*- coding: utf-8 -*-

"""Tangram Game. See Readme.md for more

TODO: Correct implementation for credits or bonus games : not an os command"""


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
                              command=project.quit)
    redem.pack()
    btn_quit.pack()

    window_geometry(advise, 500, 50)


name_pieces = ['tri1', 'tri2', 'tri_moy', 'tripe1', 'tripe2', 'carre', 'para']
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
        self.onclick(self.rotation, btn=3)
        # self.onclick(lambda x, y: print(self.name), btn=1)

        self.ondrag(self.my_ondrag)

    def rotation(self, *_) -> None:
        self.rot += 1
        self.rot %= self.modulo_rot
        self.seth(self.rot * 15)
        self.screen.update()

    def setup(self, state: tuple[tuple[float, float], int]) -> None:
        self.goto(state[0])
        self.seth(state[1] * 15)
        self.rot = state[1]
        self.screen.update()

    def my_ondrag(self, x, y):
        self.goto(x, y)
        self.screen.update()


@dataclass
class TangramShape:
    """Describes a tangram shape : positions of the pieces, rotation, etc."""

    name: str
    positions: dict[str, tuple[float, float]]
    rotations: dict[str, int]
    para_flipped: bool
    img_file: Optional[str]

    def __post_init__(self):
        if set(self.rotations) != set(self.positions):
            ValueError("positions and rotations must have the same keys")

    def piece_state(self, name: str) -> tuple[tuple[float, float], int]:
        return self.positions[name], self.rotations[name]

    def pieces_state(self) -> dict[str, tuple[tuple[float, float], int]]:
        return {name: self.piece_state(name) for name in self.rotations}

    def __getitem__(self, name: str) -> tuple[tuple[float, float], int]:
        return self.piece_state(name)


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
    _default_hints = 18

    def __init__(self):
        """Main class for the tangram game"""

        self.hints = self._default_hints

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
        # ici nous allons définir un menu pour chaque élément du tangram qui
        # permettra au joueur de personnaliser les couleurs de son jeu qui sont
        # automatiquement mises à jour grâce à la fonction color_init()
        color_labels = ["Triangle 1", "Triangle 2", "Triangle Moyen",
                        "Petit Triangle 1", "Petit Triangle 2", "Carre",
                        "Parallélogramme"]

        def menu_chose_color(var_col_piece: tkinter.StringVar) -> tkinter.Menu:
            menu_ = tkinter.Menu(color, tearoff=0)
            for j_label, j_val in self._liste_init_color:
                menu_.add_radiobutton(label=j_label, value=j_val,
                                      variable=var_col_piece,
                                      command=self.color_init)
            return menu_

        for i_label, i_color in zip(color_labels, self.l_color):
            color.add_cascade(label=i_label, menu=menu_chose_color(i_color))

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
        fichier.add_command(label="Quitter", command=project.quit)
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

        cv1.bind("<ButtonRelease-1>", self.end_move)
        cv1.bind("<Double-Button-1>", self.flip_para)

        # et pour permettre au joueur de faire le symétrique du parallélogramme

        self.s1.listen()
        # il ne reste plus qu'à attendre un évènement

    def set_shape(self, piece: Piece):
        if piece.name == 'para':
            para = ['para1', 'para2']
            piece.shape(para[self.lvl.para_flipped])
        else:
            piece.shape(piece.name)

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
            names = list(name_pieces)  # type: list[str]

            cpt = len(names)
            j = randrange(0, cpt)
            # on tire un curseur au hasard

            name = names[j]
            piece = self.dict_piece[name]
            figure = self.lvl
            piece.setup(self.lvl[name])

            if self.para_is_flipped() != figure.para_flipped \
                    and (
                    piece.shape() == "para1"
                    or piece.shape() == "para2"):
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
        # the variable `helped` is reset to 2 (see function `hint()`)
        self.hints = self._default_hints
        # call of the function init for the changes to take effect.

        for name, piece in self.dict_piece.items():
            piece.up()
            self.set_shape(piece)
            piece.setup(init_figure.piece_state(name))

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
        fond = tkinter.Label(fen3, image=pictures("end"))

        # Creation of a restart and quit button.
        # (the 'quit' one quit everything)
        restart = tkinter.Button(
            fond, image=pictures("restart"),
            command=lambda: [self.restart(), fen3.destroy()])
        bye = tkinter.Button(fond, image=pictures("quit_end"),
                             command=project.quit)

        fond.pack()
        # affichage et centrage de la fenêtre.
        restart.place(x=CONFIG_RES[self.res]["x_res"],
                      y=CONFIG_RES[self.res]["y_res"])
        bye.place(x=CONFIG_RES[self.res]["xby"],
                  y=CONFIG_RES[self.res]["yby"])
        window_geometry(fen3, *CONFIG_RES[self.res]["end_window"])

    @staticmethod
    def nearly_pos(piece: Piece, pos: tuple[float, float], dist_lim=5) -> bool:
        dist = distance(pos, piece.position())
        return dist <= dist_lim

    def is_solved(self, piece: Piece, sol) -> bool:
        if not self.nearly_pos(piece, sol[0]):
            return False
        piece.goto(sol[0])
        self.s1.update()
        return piece.rot == sol[1]

    def check_one(self, piece: Piece) -> bool:
        sol = self.lvl[piece.name]
        return self.is_solved(piece, sol)

    def check_pairs(self, piece1: Piece, piece2: Piece) -> bool:
        sol1, sol2 = self.lvl[piece1.name], self.lvl[piece2.name]
        if self.is_solved(piece1, sol1) and self.is_solved(piece2, sol2):
            return True
        return self.is_solved(piece1, sol2) and self.is_solved(piece2, sol1)

    def check_end(self) -> bool:
        """Cette fonction détecte si le niveau est terminé ou non"""
        # if a piece is in position with dist < dist_lim,
        # we place it automatically
        if not self.check_pairs(self.dict_piece['tri1'],
                                self.dict_piece['tri2']):
            return False
        if not self.check_pairs(self.dict_piece['tripe1'],
                                self.dict_piece['tripe2']):
            return False
        for one in ['tri_moy', 'carre', 'para']:
            if not self.check_one(self.dict_piece[one]):
                return False
        # Last test checking if the parallelogram must be reversed or not.
        return self.para_is_flipped() == self.lvl.para_flipped

    def end_move(self, _):
        if not self.check_end():
            return None
        self.s1.update()
        self.end_tangram_level()

    def para_is_flipped(self) -> bool:
        para = self.dict_piece['para']
        return para.shape() == 'para2'

    def flip_para(self, *_) -> None:
        """Récupère la forme de l'objet C_para et lui assigne sa forme
         symétrique"""
        para = self.dict_piece['para']
        shape = para.shape()
        para.shape({"para2": "para1", "para1": "para2"}[shape])
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
    if res not in ["1000x700", '500x350']:
        raise ValueError(
            "Seules les résolutions 1000x700 ou 500x350 sont prévues.")


files_img = {"base_menu": "Tangram.gif", "main": "main.gif",
             "play": "Jouer.gif",
             "credits": "Crédits.gif", "quit": "Quitter.gif", "end": "end.gif",
             "restart": "reco.gif", "quit_end": "quitter_end.gif"}

# configuration de la taille des fenêtres principales
# et de la fenêtre de fin de jeu
CONFIG_RES = {
    "1000x700": {
        "window": (1000, 700), "end_window": (300, 210), "cote": 200,
        "x_btn": 410, "y_btn": 252, "x_btn1": 400, "y_btn1": 375, "x_btn2": 400,
        "y_btn2": 490, "x_res": 5, "y_res": 140, "xby": 180, "yby": 137
    },
    "500x350": {
        "window": (500, 350), "end_window": (150, 105), "cote": 100,
        "x_btn": 205, "y_btn": 126, "x_btn1": 200, "y_btn1": 188, "x_btn2": 200,
        "y_btn2": 245, "x_res": 3, "y_res": 70, "xby": 90, "yby": 69
    }
}
position_res = {
    '1000x700': {
        'CARRE': {'tri1': (409.00, 2.00), 'tri2': (308.00, -99.00),
                  'tri_moy': (257.00, 52.00), 'tripe1': (358.00, 103.00),
                  'tripe2': (258.00, 1.00), 'carre': (308.00, 53.00),
                  'para': (232.00, -34.00)},
        'CANARD': {'tri1': (-161.00, -21.00), 'tri2': (-160.00, -21.00),
                   'tri_moy': (-262.00, -91.00), 'tripe1': (-384.00, 10.00),
                   'tripe2': (-60.00, 30.00), 'carre': (-334.00, 61.00),
                   'para': (-309.00, -25.00)},
        'PROSTERNE': {'tri1': (-230.00, 26.00), 'tri2': (-154.00, 18.00),
                      'tri_moy': (-292.00, -21.00), 'tripe1': (-304.00, 28.00),
                      'tripe2': (-86.00, -107.00), 'carre': (-39.00, -25.00),
                      'para': (-319.00, -55.00)},
        'LAPIN': {'tri1': (-281.00, -115.00), 'tri2': (-251.00, -44.00),
                  'tri_moy': (-253.00, 128.00), 'tripe1': (-200.00, -81.00),
                  'tripe2': (-250.00, -30.00), 'carre': (-216.00, 59.00),
                  'para': (-198.00, 137.00)},
        'FIGURE': {'tri1': (-223.00, 16.00), 'tri2': (-240.00, -111.00),
                   'tri_moy': (-228.00, 138.00), 'tripe1': (-285.00, 26.00),
                   'tripe2': (-322.00, 33.00), 'carre': (-219.00, -39.00),
                   'para': (-184.00, 131.00)}
    },
    '500x350': {
        'CARRE': {'tri1': (204.5, 1.0), 'tri2': (154.0, -49.5),
                  'tri_moy': (128.5, 26.0), 'tripe1': (179.0, 51.5),
                  'tripe2': (129.0, 0.5), 'carre': (154.0, 26.5),
                  'para': (116.0, -17.0)},
        'CANARD': {'tri1': (-80.5, -10.5), 'tri2': (-80.0, -10.5),
                   'tri_moy': (-131.0, -45.5), 'tripe1': (-192.0, 5.0),
                   'tripe2': (-30.0, 15.0), 'carre': (-167.0, 30.5),
                   'para': (-154.5, -12.5)},
        'PROSTERNE': {'tri1': (-115.0, 13.0), 'tri2': (-77.0, 9.0),
                      'tri_moy': (-146.0, -10.5), 'tripe1': (-152.0, 14.0),
                      'tripe2': (-43.0, -53.5), 'carre': (-19.5, -12.5),
                      'para': (-159.5, -27.5)},
        'LAPIN': {'tri1': (-140.5, -57.5), 'tri2': (-125.5, -22.0),
                  'tri_moy': (-126.5, 64.0), 'tripe1': (-100.0, -40.5),
                  'tripe2': (-125.0, -15.0), 'carre': (-108.0, 29.5),
                  'para': (-99.0, 68.5)},
        'FIGURE': {'tri1': (-111.5, 8.0), 'tri2': (-120.0, -55.5),
                   'tri_moy': (-114.0, 69.0), 'tripe1': (-142.5, 13.0),
                   'tripe2': (-161.0, 16.5), 'carre': (-109.5, -19.5),
                   'para': (-92.0, 65.5)}
    }
}
# tableaux contenant toutes les informations pour la réalisation des niveaux
# ( 1: emplacement, 2: rotation, 3: `reverse` value,
#  4: emplacement de l'image de fond associée)
CARRE = TangramShape('CARRE', position_res[res]['CARRE'],
                     {'tri1': 0, 'tri2': 18, 'tri_moy': 18, 'tripe1': 6,
                      'tripe2': 12, 'carre': 3, 'para': 6}, False, None)
CANARD = TangramShape('CANARD', position_res[res]['CANARD'],
                      {'tri1': 0, 'tri2': 12, 'tri_moy': 15, 'tripe1': 12,
                       'tripe2': 6, 'carre': 3, 'para': 6}, False,
                      f"HT/{res}/canard.gif")
PROSTERNE = TangramShape('PROSTERNE', position_res[res]['PROSTERNE'],
                         {'tri1': 16, 'tri2': 13, 'tri_moy': 13, 'tripe1': 19,
                          'tripe2': 16, 'carre': 2, 'para': 1}, False,
                         f"HT/{res}/prosterne.gif")
LAPIN = TangramShape('LAPIN', position_res[res]['LAPIN'],
                     {'tri1': 3, 'tri2': 0, 'tri_moy': 21, 'tripe1': 0,
                      'tripe2': 12, 'carre': 0, 'para': 4}, False,
                     f"HT/{res}/lapin.gif")
FIGURE = TangramShape('FIGURE', position_res[res]['FIGURE'],
                      {'tri1': 15, 'tri2': 9, 'tri_moy': 0, 'tripe1': 12,
                       'tripe2': 9, 'carre': 3, 'para': 9}, True,
                      f"HT/{res}/figure.gif")


# Window starting the project

class MyPhotoImg(tkinter.PhotoImage):
    """Trick to avoid problems with garbage collector.

    There is a bug in PhotoImage implementation, with the garbage collector:
    for example if we were to do :

    def make_label():
        img = tkinter.PhotoImage(file=file_name)
        return tkinter.Label(master, image=img)
    lab = make_label()

    then the garbage collector will (??!!) delete the image.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.img = self  # no more bug


def pictures(label: str):
    name_file = files_img[label]
    return MyPhotoImg(file=f"HT/{res}/{name_file}")


class Project(tkinter.Tk):
    """Base of the project"""

    def __init__(self):
        super().__init__()
        self.title("Tangram Project")

        self.start_window = tkinter.Label(self, image=pictures("base_menu"))

        window_geometry(self, *CONFIG_RES[res]["window"])
        # centrage de la fenêtre
        self.start_window.pack(side='top', fill='both', expand=1)
        # affichage du fond

        # après 2 secondes, on change l'image de fond et on affiche les boutons
        # cette ligne permet de créer l'animation du début
        self.after(2000, self.show_menu)

    def show_menu(self):
        btn = tkinter.Button(self.start_window, text="Jouer",
                             command=Tangram, image=pictures("play"))
        btn1 = tkinter.Button(self.start_window, text="README (Crédits)",
                              command=lambda: os.system("okular README.md"),
                              image=pictures("credits"))
        btn2 = tkinter.Button(self.start_window, text="Quitter",
                              command=self.quit, image=pictures("quit"))
        # Création de 3 boutons permettant de jouer au tangram,
        # de quitter le jeu ou d'afficher dans gedit le fichier crédits.txt
        self.start_window.configure(image=pictures("main"))
        btn.place(x=CONFIG_RES[res]["x_btn"], y=CONFIG_RES[res]["y_btn"])
        btn1.place(x=CONFIG_RES[res]["x_btn1"], y=CONFIG_RES[res]["y_btn1"])
        btn2.place(x=CONFIG_RES[res]["x_btn2"], y=CONFIG_RES[res]["y_btn2"])


project = Project()
# on entre dans la boucle principale...
project.config()
project.mainloop()
# ... et on détruit la fenêtre principale si l'on en sort.
project.destroy()
