from tkinter import Tk, Canvas
import src.globals as gb
from src.box import Current_box, And_box



def reverse_find(dic, value):
    for key in dic:
        if dic[key] == value:
            return key
    raise ValueError


class Window(Tk):
    def __init__(self):
        # INIT WINDOW
        Tk.__init__(self)
        self.attributes("-topmost", True)
        self.geometry("{}x{}+10+10".format(gb.WINDOW_WIDTH, gb.WINDOW_HEIGHT))
        self.fond = Canvas(self, width = gb.WINDOW_WIDTH, height = gb.WINDOW_HEIGHT, bg = gb.WINDOW_BG)
        self.fond.pack()
        self.fond.create_line(50, 0, 50, gb.WINDOW_HEIGHT, width = 2, fill = "black")
        self.fond.create_line(gb.WINDOW_WIDTH - 50, 0, gb.WINDOW_WIDTH - 50, gb.WINDOW_HEIGHT, width = 2, fill = "black")

        # ATTRIBUTS
        self.main_box = Current_box(self)
        self.boxes = set()
        self.links = set()
        self.nodes = set()
        self.last_in = []
        self.last_out = []
        self.selected = None

        # BINDINGS
        self.bind("<Control-Key-S>", self.save_conf)
        self.bind("<Up>", self.add_input)
        self.bind("<Down>", self.remove_input)
        self.bind("<Control-Up>", self.add_output)
        self.bind("<Control-Down>", self.remove_output)
        self.bind("<Key-a>", self.and_gate)
        self.bind("<Key-o>", self.or_gate)
        self.bind("<Motion>", self.move)

        # MAINLOOP
        self.mainloop()

    def move(self, evt):
        pass

    def save_conf(self, evt):
        pass

    def and_gate(self, evt):
        print("ajoute d'une porte AND")
        gate = And_box(self, (evt.x, evt.y))
        id = gate.draw()
        self.boxes.add(id)

    def or_gate(self, evt):
        print("ajoute d'une porte OR")

    def add_input(self, evt):
        print("Ajout d'une node input")
        id = self.main_box.add_input(self)
        self.last_in += [id]
        self.nodes.add(id)
    def remove_input(self, evt):
        print("Retrait d'une node input")
        node = self.main_box.remove_input(self)
        if node is not None:
            id = self.last_in.pop(-1)
            self.nodes.remove(id)
            self.fond.delete(id)
    def add_output(self, evt):
        print("Ajout d'une node output")
        id = self.main_box.add_output(self)
        self.last_out += [id]
        self.nodes.add(id)
    def remove_output(self, evt):
        print("Retrait d'une node output")
        node = self.main_box.remove_output(self)
        if node is not None:
            id = self.last_out.pop(-1)
            self.nodes.remove(id)
            self.fond.delete(id)

    # def erase(self):
    #     print("Effacement de l'écran")
    #     for node in self.nodes:
    #         self.fond.delete(node)
    #     for box in self.boxes:
    #         self.fond.delete(box)
    #     for link in self.links:
    #         self.fond.delete(link)

    # def redraw(self):
    #     print("Redessin de l'écran")
    #     self.erase()
    #     for link in self.links:
    #         self.links[link].draw(self)
    #     for box in self.boxes:
    #         self.boxes[box].draw(self)
    #     for node in self.nodes:
    #         self.nodes[node].draw(self)





def run():
    fen = Window()
