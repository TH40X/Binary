from tkinter import Tk, Canvas
import src.globals as gb
from src.gate import Current_gate, And_gate, Gate
from src.node import Node, Input_node, Output_node



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
        self.main_gate = Current_gate(self)
        self.main_gate.fen = self
        self.gates = set()
        self.selected = None
        self.link_node = None
        self.link_id = None

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
        if self.link_id:
            # mise à jour de l'affichage du link
            self.fond.coords(self.link_id, self.link_node.center[0], self.link_node.center[1], evt.x, evt.y)
            self.fond.tag_lower(self.link_id)

    def save_conf(self, evt):
        pass

    def draw_node(self, node):
        """
        Dessine une node et ajoute son id à la liste des nodes
        """
        x, y = node.center
        id = self.fond.create_oval(x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE, outline = "black", width = 3, fill = "white")
        self.fond.tag_bind(id, "<Button-1>", node.clic)
        self.fond.tag_bind(id, "<Button-3>", node.r_clic)
        return id

    def update(self, item):
        print("Updating {}".format(type(item)))
        print("{}{}".format(Node, item.__class__.__bases__))
        target_class = item.__class__.__bases__

        if Node in target_class or Output_node in target_class or Input_node in target_class:
            #c'est une node
            print(item.center)
            x, y = item.center
            self.fond.coords(item.id, x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE)
            self.fond.itemconfig(item.id, fill = "red" if item.active else "white")

            if type(item) == Output_node:
                for node in item.next:
                    self.update(node)
            elif type(item) == Input_node:
                # on a update une node appartenant à une gate : on update cette gate
                if type(item.gate) != Current_gate:
                    self.update(item.gate)

        elif Gate in target_class:
            #c'est une gate
            if type(item) == Current_gate:
                for node in item.outputs:
                    self.update(node)
                for node in item.inputs:
                    self.update(node)
            else:
                x, y = item.center
                self.fond.coords(item.id, x - gb.BOX_WIDTH, y - item.height, x + gb.BOX_WIDTH, y + item.height)

                # on update que la node de sortie
                for node in item.outputs:
                    self.update(node)

    def draw_gate(self, gate):
        """
        Affiche une gate et les nodes associées
        """
        x, y = gate.center
        id = self.fond.create_rectangle(x - gb.BOX_WIDTH, y - gate.height, x + gb.BOX_WIDTH, y + gate.height, outline = "black", fill = "gray", width = 3)
        self.fond.tag_bind(id, "<Button-1>", gate.clic)
        self.gates.add(id)

        name_id = self.fond.create_text(x, y, text = gate.name)
        gate.name_id = name_id

        for node in gate.inputs:
            id = self.draw_node(node)
            node.id = id
        for node in gate.outputs:
            id = self.draw_node(node)
            node.id = id

        return id

    def and_gate(self, evt):
        print("ajoute d'une porte AND")
        gate = And_gate(self, (evt.x, evt.y))
        id = self.draw_gate(gate)
        gate.id = id
        self.update(gate)

    def or_gate(self, evt):
        print("ajoute d'une porte OR")

    def add_input(self, evt):
        print("Ajout d'une node input")
        node = self.main_gate.add_input()
        id = self.draw_node(node)
        node.id = id
        self.update(self.main_gate)
    def remove_input(self, evt):
        print("Retrait d'une node input")
        node = self.main_gate.remove_input()
        if node is not None:
            self.fond.delete(node.id)
            self.update(self.main_gate)
    def add_output(self, evt):
        print("Ajout d'une node output")
        node = self.main_gate.add_output()
        id = self.draw_node(node)
        node.id = id
        self.update(self.main_gate)
    def remove_output(self, evt):
        print("Retrait d'une node output")
        node = self.main_gate.remove_output()
        if node is not None:
            self.fond.delete(node.id)
            self.update(self.main_gate)





def run():
    fen = Window()
