from tkinter import Tk, Canvas
import src.globals as gb
from src.gate import Current_gate, And_gate, Or_gate, Gate
from src.node import Node, Input_node, Output_node, Main_input_node



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
        self.link = None

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
        if self.link:
            # mise à jour de l'affichage du link
            self.fond.coords(self.link.id, self.link.node1.center[0], self.link.node1.center[1], evt.x, evt.y)
            self.fond.tag_lower(self.link.id)

    def save_conf(self, evt):
        pass

    def draw_link(self, link):
        """
        Dessine un link
        """
        x, y = link.node1.center
        id = self.fond.create_line(x, y, x, y, fill = "black", width = 2)
        return id

    def draw_node(self, node):
        """
        Dessine une node
        """
        x, y = node.center
        id = self.fond.create_oval(x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE, outline = "black", width = 3, fill = "white")
        self.fond.tag_bind(id, "<Button-1>", node.clic)
        self.fond.tag_bind(id, "<Button-3>", node.r_clic)
        self.fond.tag_bind(id, "<Control-Button-1>", node.delete)
        node.text = self.fond.create_text(x, y, text = str(id))
        return id

    def update(self, item):
        target_class = item.__class__.__bases__

        if Node in target_class or Output_node in target_class or Input_node in target_class:
            print("Updating node {}".format(item.id))
            #c'est une node
            x, y = item.center
            self.fond.coords(item.id, x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE)
            self.fond.itemconfig(item.id, fill = "red" if item.active else "white")
            self.fond.coords(item.text, x, y)

            for link in item.next_links:
                x1, y1 = link.node1.center
                x2, y2 = link.node2.center
                self.fond.coords(link.id, x1, y1, x2, y2)
            if item.prev_link:
                x1, y1 = item.prev_link.node1.center
                x2, y2 = item.prev_link.node2.center
                self.fond.coords(item.prev_link.id, x1, y1, x2, y2)

        elif Gate in target_class:
            #c'est une gate
            if type(item) == Current_gate:
                #Permet le placement des nodes principales du circuit
                for node in item.inputs:
                    self.update(node)
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
        gate = Or_gate(self, (evt.x, evt.y))
        id = self.draw_gate(gate)
        gate.id = id
        self.update(gate)

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
