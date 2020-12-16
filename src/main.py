from tkinter import Tk, Canvas
import src.globals as gb
from src.gate import Current_gate, And_gate, Not_gate, Gate
from src.node import Node, Input_node, Output_node, Main_input_node
import os
from src.gate_generator import Generator
from src.link import Link


def GB_INFO(evt):
    print("____________________________________________________________")
    print("Nombre totale de portes créées : {}".format(gb.GATE_NUMBER))
    print("Nombre totale de node créées : {}".format(gb.NODE_NUMBER))
    print("Nombre de nodes mises à jour sur la dernière update : {}".format(gb.UPDATE_NUMBER))

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
        self.bindings = {"<Control-Key-s>" : self.save_conf_name,
                         "<Up>" : self.add_input,
                         "<Down>" : self.remove_input,
                         "<Control-Up>" : self.add_output,
                         "<Control-Down>" : self.remove_output,
                         "<Motion>" : self.move,
                         "<ButtonRelease-1>" : self.release_clic,
                         "<Button-2>" : self.cancel_link,
                         "<Button-1>" : GB_INFO}
        self.enable_bindings()

        # LOAD GATES
        self.load_below_gates()

        # MAINLOOP
        self.mainloop()

    ######################### BINDINGS #########################
    def enable_bindings(self):
        if gb.DEBUG:print("Bindings enabled")
        for to_bind in self.bindings:
            self.bind(to_bind, self.bindings[to_bind])
    def disable_bindings(self):
        if gb.DEBUG:print("Bindings disabled")
        for to_unbind in self.bindings:
            self.unbind(to_unbind)

    def save_pressed_key(self, evt):
        lettre = evt.char.upper()
        if lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 ":
            #la lettre est autorisée
            self.gate_name += lettre
            self.fond.itemconfig(self.name_id, text = self.gate_name)

    ######################### MOVE EVENTS #########################
    def cancel_link(self, evt):
        if self.link:
            self.link.delete_aff()
            self.link = None

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
            self.link.points_list[-1] = (evt.x, evt.y)
            self.update(self.link)

    ######################### GATE GENERATOR #########################
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

    ######################### SAVING CONFIGURATION #########################
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
        self.reload_below_gate()

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

    ######################### DRAWING #########################
    def draw_link(self, link):
        """
        Dessine un link
        """
        try:
            x, y = link.points_list[-1].center
        except:
            x, y = link.points_list[-1]
        id = self.fond.create_line(x, y, x, y, fill = "white", width = 2)
        self.fond.tag_bind(id, "<Button-3>", link.r_clic)
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
        self.fond.tag_bind(node.text, "<Button-1>", node.clic)
        self.fond.tag_bind(node.text, "<Button-3>", node.r_clic)
        self.fond.tag_bind(node.text, "<Button-2>", node.delete)
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

    ######################### UPDATE DISPLAY #########################
    def update_all(self):
        """
        Deux update sont nécéssaire pour que les flip flop marchent
        """
        gb.PRE_UPDATE()
        for node in self.main_gate.inputs:
            node.need_previous()
        for gate in self.gates:
            #Actualise toutes les gates
            for output_node in gate.outputs:
                output_node.need_previous()
        for node in self.main_gate.outputs:
            node.need_previous()
        # Deuxieme update
        gb.UPDATE_ID += 1
        for node in self.main_gate.inputs:
            node.need_previous()
        for gate in self.gates:
            #Actualise toutes les gates
            for output_node in gate.outputs:
                output_node.need_previous()
        for node in self.main_gate.outputs:
            node.need_previous()

    def update(self, item):
        target_class = item.__class__.__bases__

        if type(item) == Link:
            try:
                x2, y2 = item.points_list[-1]
            except:
                x2, y2 = item.points_list[-1].center
            try:
                x1, y1 = item.points_list[-2]
            except:
                x1, y1 = item.points_list[-2].center
            self.fond.coords(item.id_list[-1], x1, y1, x2, y2)
            try:
                x2, y2 = item.points_list[0]
            except:
                x2, y2 = item.points_list[0].center
            try:
                x1, y1 = item.points_list[1]
            except:
                x1, y1 = item.points_list[1].center
            self.fond.coords(item.id_list[0], x1, y1, x2, y2)
            if item.get_input():
                item.active = item.get_input().active
            for link_seg_id in item.id_list:
                self.fond.itemconfig(link_seg_id, fill = "red" if item.active else "white")
            self.fond.tag_lower(item.id_list[-1])

        elif Node in target_class or Output_node in target_class or Input_node in target_class:
            #c'est une node
            if item.get_type() in ("main_output", "input") and not item.prev:
                item.active = False
            x, y = item.center
            self.fond.coords(item.id, x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE)
            self.fond.itemconfig(item.id, fill = "red" if item.active else "white")
            self.fond.coords(item.text, x, y)

            for link in item.next_links:
                self.update(link)
            if item.prev_link:
                self.update(item.prev_link)

        else:
            #c'est une gate
            if item.name != "MAIN":
                #c'est une gate normale
                x, y = item.center
                dx, dy = item.delta_x, item.delta_y
                self.fond.coords(item.id, x - gb.BOX_WIDTH, y - item.height, x + gb.BOX_WIDTH, y + item.height)
                self.fond.coords(item.name_id, x, y)

            for node in item.inputs:
                self.update(node)
            for node in item.outputs:
                self.update(node)

    ######################### ADD/REMOVE INPUTS/OUTPUTS #########################
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
            self.fond.delete(node.text)
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
            self.fond.delete(node.text)
            self.update(self.main_gate)





def run():
    fen = Window()
