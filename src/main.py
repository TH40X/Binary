from tkinter import Tk, Canvas
import src.globals as gb
from src.gate import Current_gate, And_gate, Not_gate, Gate
from src.node import Node, Input_node, Output_node, Main_input_node
import os
from src.gate_generator import Generator



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
        self.geometry("{}x{}+10+10".format(gb.WINDOW_WIDTH, gb.WINDOW_HEIGHT + 50))
        self.fond = Canvas(self, width = gb.WINDOW_WIDTH, height = gb.WINDOW_HEIGHT + 50, bg = gb.WINDOW_BG)
        self.fond.pack()
        self.fond.create_line(50, 0, 50, gb.WINDOW_HEIGHT, width = 2, fill = "black")
        self.fond.create_line(gb.WINDOW_WIDTH - 50, 0, gb.WINDOW_WIDTH - 50, gb.WINDOW_HEIGHT, width = 2, fill = "black")

        # ATTRIBUTS
        self.main_gate = Current_gate(self)
        self.main_gate.fen = self
        self.main_gate.name = 'MAIN'
        self.gates = set()
        self.selected = None
        self.link = None
        self.generators = set()

        # BINDINGS
        self.enable_bindings()

        # LOAD GATES
        self.load_below_gates()

        # MAINLOOP
        self.mainloop()

    def enable_bindings(self):
        if gb.DEBUG:print("Bindings enabled")
        self.bind("<Control-Key-s>", self.save_conf_name)
        self.bind("<Up>", self.add_input)
        self.bind("<Down>", self.remove_input)
        self.bind("<Control-Up>", self.add_output)
        self.bind("<Control-Down>", self.remove_output)
        self.bind("<Motion>", self.move)
        self.bind("<ButtonRelease-1>", self.release_clic)
    def disable_bindings(self):
        if gb.DEBUG:print("Bindings disabled")
        self.unbind("<Control-Key-s>")
        self.unbind("<Up>")
        self.unbind("<Down>")
        self.unbind("<Control-Up>")
        self.unbind("<Control-Down>")
        self.unbind("<Motion>")
        self.unbind("<ButtonRelease-1>")

    def release_clic(self, evt):
        self.selected = None

    def move(self, evt):
        if self.selected:
            dx = self.selected.delta_x
            dy = self.selected.delta_y
            self.selected.center = (evt.x + dx, evt.y + dy)
            self.selected.update_nodes_coords()
            self.update(self.selected)
        if self.link:
            # mise à jour de l'affichage du link
            self.fond.coords(self.link.id, self.link.node1.center[0], self.link.node1.center[1], evt.x, evt.y)
            self.fond.tag_lower(self.link.id)

    def load_below_gates(self):
        for i, gate_name in enumerate(os.listdir("lib/structs/")):
            x = i * 120 + 10
            y = gb.WINDOW_HEIGHT + 25
            generator = Generator(gate_name, self)
            self.generators.add(generator)
            id = self.fond.create_rectangle(x, y - 20, x + 100, y + 20, width = 2, fill = "gray")
            generator.id = id
            name_id = self.fond.create_text(x + 50, y, text = gate_name)
            generator.name_id = name_id
            self.fond.tag_bind(id, "<Button-1>", generator.create_gate)
            self.fond.tag_bind(name_id, "<Button-1>", generator.create_gate)

    def reload_below_gate(self):
        for generator in self.generators:
            self.fond.delete(generator.id)
            self.fond.delete(generator.name_id)
        self.load_below_gates()

    def save_conf_name(self, evt):
        """
        Permet de selectionner le nom de la gate créée
        """
        self.disable_bindings()
        x, y = gb.WINDOW_WIDTH / 2, gb.WINDOW_HEIGHT / 2
        self.rectangle_name_id = self.fond.create_rectangle(x - 50, y - 25, x + 50, y + 25, width = 3, fill = "white")
        self.gate_name = ""
        self.name_id = self.fond.create_text(x, y, text = "")
        self.bind("<KeyPress>", self.save_pressed_key)
        self.bind("<Return>", self.save_conf)
        self.bind("<Escape>", self.cancel_save_conf)

    def cancel_save_conf(self, evt):
        self.clean_save_conf()
    def save_conf(self, evt):
        if not self.gate_name in os.listdir("lib/structs/"):
            with open("lib/structs/" + self.gate_name, "w") as f:
                # Ajoute les gate au fichier
                for gate in self.gates:
                    f.write(str(gate))

                # Ajoute les nodes d'entrée et de sortie au fichier
                for node in self.main_gate.inputs:
                    f.write(str(node))
                for node in self.main_gate.outputs:
                    f.write(str(node))

                #ajoute les nodes de chaque gate au fichier
                for gate in self.gates:
                    for node in gate.inputs:
                        f.write(str(node))
                    for node in gate.outputs:
                        f.write(str(node))
        self.clean_save_conf()

    def clean_save_conf(self):
        self.unbind("<KeyPress>")
        self.unbind("<Return>")
        self.unbind("<Escape>")
        self.fond.delete(self.rectangle_name_id)
        self.fond.delete(self.name_id)
        self.name_id = None
        self.rectangle_name_id = None
        self.gate_name = ""
        self.enable_bindings()

    def save_pressed_key(self, evt):
        lettre = evt.char.upper()
        if lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 ":
            #la lettre est autorisée
            self.gate_name += lettre
            self.fond.itemconfig(self.name_id, text = self.gate_name)

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
        self.fond.tag_bind(id, "<Button-2>", node.delete)
        node.text = self.fond.create_text(x, y, text = str(id))
        return id

    def draw_gate(self, gate):
        """
        Affiche une gate et les nodes associées
        """
        x, y = gate.center
        id = self.fond.create_rectangle(x - gb.BOX_WIDTH, y - gate.height, x + gb.BOX_WIDTH, y + gate.height, outline = "black", fill = "gray", width = 3)
        gate.id = id
        self.fond.tag_bind(id, "<Button-1>", gate.clic)
        self.fond.tag_bind(id, "<Button-2>", gate.delete)

        name_id = self.fond.create_text(x, y, text = gate.name)
        gate.name_id = name_id
        self.fond.tag_bind(name_id, "<Button-1>", gate.clic)
        self.fond.tag_bind(name_id, "<Button-2>", gate.delete)

        for node in gate.inputs:
            id2 = self.draw_node(node)
            node.id = id2
        for node in gate.outputs:
            id3 = self.draw_node(node)
            node.id = id3

        return id

    def update(self, item):
        target_class = item.__class__.__bases__

        if Node in target_class or Output_node in target_class or Input_node in target_class:
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
            else:
                #c'est une gate normale
                x, y = item.center
                dx, dy = item.delta_x, item.delta_y
                self.fond.coords(item.id, x - gb.BOX_WIDTH, y - item.height, x + gb.BOX_WIDTH, y + item.height)
                self.fond.coords(item.name_id, x, y)
                for node in item.inputs:
                    self.update(node)
                for node in item.outputs:
                    self.update(node)


    def and_gate(self, center):
        if gb.DEBUG:print("ajoute d'une porte AND")
        gate = And_gate(self, (evt.x, evt.y))
        input1 = Input_node((0, 0), gate, self)
        input2 = Input_node((0, 0), gate, self)
        output = Output_node((0, 0), gate, self)
        Gate.__init__(gate, [input1, input2], [output])
        gate.update_nodes_coords()

        self.gates.add(gate)
        id = self.draw_gate(gate)
        self.update(gate)

    def not_gate(self, evt):
        if gb.DEBUG:print("ajoute d'une porte OR")
        gate = Not_gate(self, (evt.x, evt.y))
        input = Input_node((0, 0), gate, self)
        output = Output_node((0, 0), gate, self)
        Gate.__init__(gate, [input], [output])
        gate.update_nodes_coords()

        self.gates.add(gate)
        id = self.draw_gate(gate)
        self.update(gate)

    def add_input(self, evt):
        if gb.DEBUG:print("Ajout d'une node input")
        node = self.main_gate.add_input()
        id = self.draw_node(node)
        node.id = id
        self.update(self.main_gate)
    def remove_input(self, evt):
        if gb.DEBUG:print("Retrait d'une node input")
        node = self.main_gate.remove_input()
        if node is not None:
            self.fond.delete(node.id)
            self.update(self.main_gate)
    def add_output(self, evt):
        if gb.DEBUG:print("Ajout d'une node output")
        node = self.main_gate.add_output()
        id = self.draw_node(node)
        node.id = id
        self.update(self.main_gate)
    def remove_output(self, evt):
        if gb.DEBUG:print("Retrait d'une node output")
        node = self.main_gate.remove_output()
        if node is not None:
            self.fond.delete(node.id)
            self.update(self.main_gate)





def run():
    fen = Window()
