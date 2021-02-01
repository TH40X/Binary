from tkinter import Tk, Canvas
import src.globals as gb
from src.gate import And_gate, Not_gate, Gate, New_gate
from src.node import Node, Input_node, Output_node, Main_input_node, Main_output_node
import os
from src.gate_generator import Generator
from src.link import Link


def GB_INFO(evt):
    gb.debug("____________________________________________")
    gb.debug("Nombre totale de portes créées : {}".format(gb.GATE_NUMBER))
    gb.debug("Nombre totale de node créées : {}".format(gb.NODE_NUMBER))
    gb.debug("Nombre de nodes mises à jour sur la dernière update : {}".format(gb.UPDATE_NUMBER))

def reverse_find(dic, value):
    for key in dic:
        if dic[key] == value:
            return key
    raise ValueError


class Window(Tk):
    def __init__(self):
        # INIT WINDOW
        Tk.__init__(self)
        self.geometry("{}x{}+10+10".format(gb.WINDOW_WIDTH, gb.WINDOW_HEIGHT))
        self.fond = Canvas(self, width = gb.WINDOW_WIDTH, height = gb.WINDOW_HEIGHT, bg = gb.WINDOW_BG)
        self.fond.pack()
        self.real_bg = self.fond.create_rectangle(0, 0, gb.WINDOW_WIDTH, gb.WINDOW_HEIGHT, fill = gb.WINDOW_BG)
        self.init_input_output()

        # ATTRIBUTS
        self.main_gate = New_gate(self, "MAIN")
        Gate.__init__(self.main_gate, [], [])
        self.gates = set()
        self.selected = None
        self.link = None
        self.generators = set()
        self.gate_gen_x = 0
        self.max_gate_gen_x = 0
        self.node_select = set()
        self.inout_frame = (0, 0, 0, 0)
        self.inout_pos = (0, 0)

        # BINDINGS
        self.bindings = {"<Control-Key-s>" : self.save_conf_name,
                         "<Motion>" : self.move,
                         "<ButtonRelease-1>" : self.release_clic,
                         "<Button-2>" : self.cancel_link,
                         "<Button-1>" : GB_INFO,
                         "<MouseWheel>" : self.scroll, # for windows
                         "<Button-4>" : self.scroll, # for linux
                         "<Button-5>" : self.scroll # for linux
                         }
        self.enable_bindings()

        # LOAD GATES
        self.load_below_gates()

        # MAINLOOP
        self.after(100, self.clock_update)
        self.mainloop()

    ######################### INPUT/OUTPUT #########################

    def init_input_output(self):
        self.input_line = self.fond.create_rectangle(0, gb.INPUT_HEIGHT, gb.WINDOW_WIDTH, gb.INPUT_HEIGHT, width = 20, fill = "black")
        self.fond.tag_bind(self.input_line, "<Button-3>", self.input_select)
        self.fond.tag_bind(self.input_line, "<Button-1>", self.add_single_input)
        self.output_line = self.fond.create_rectangle(0, gb.WINDOW_HEIGHT - gb.OUTPUT_HEIGHT, gb.WINDOW_WIDTH, gb.WINDOW_HEIGHT - gb.OUTPUT_HEIGHT, width = 20, fill = "black")
        self.fond.tag_bind(self.output_line, "<Button-3>", self.output_select)
        self.fond.tag_bind(self.output_line, "<Button-1>", self.add_single_output)

    def order_inputs_outputs(self):
        self.main_gate.inputs.sort(key = lambda x : x.center[0])
        self.main_gate.outputs.sort(key = lambda x : x.center[0])

    def clean_select(self):
        for id in self.node_select:
            self.fond.delete(id)
        self.node_select = set()
        self.inout_pos = (0, 0)
        self.inout_frame = (0, 0, 0, 0)

    def load_node_choice(self, x, y, node_type, in_out):
        table = {"input" : {"Single" : self.add_single_input, "Count" : self.add_count_input, "Clock" : self.add_clock_input},
                 "output" : {"Single" : self.add_single_output, "Count" : self.add_count_output}}
        node_frame = self.fond.create_rectangle(x, y, x + 60, y + 30)
        self.node_select.add(node_frame)
        self.fond.tag_bind(node_frame, "<Button-1>", table[in_out][node_type])

        node_text = self.fond.create_text(x + 30, y + 15, text = node_type)
        self.node_select.add(node_text)
        self.fond.tag_bind(node_text, "<Button-1>", table[in_out][node_type])

    ## _________________ INPUT _____________________ ##

    def input_select(self, evt):
        x = min(evt.x, gb.WINDOW_WIDTH - 70)
        y = evt.y
        self.inout_pos = (evt.x, evt.y)
        frame_id = self.fond.create_rectangle(x - 3, y - 3, x + 63, y + 97, fill = "lightgray")
        self.inout_frame = (x - 3, y - 3, x + 63, y + 97)
        self.node_select.add(frame_id)

        self.load_node_choice(x, y, "Single", "input")
        self.load_node_choice(x, y + 32, "Count", "input")
        self.load_node_choice(x, y + 64, "Clock", "input")

    def add_single_input(self, evt):
        if not self.inout_pos[0]:
            self.inout_pos = (evt.x, evt.y)
        node = Main_input_node(self.main_gate, self)
        node.center = (self.inout_pos[0], gb.INPUT_HEIGHT)
        self.main_gate.inputs += [node]
        self.draw_node(node)
        self.fond.tag_bind(node.id, "<Button-2>", node.destroy)
        self.clean_select()

    def add_count_input(self, evt):
        node = Main_input_node(self.main_gate, self)
        node.center = (self.inout_pos[0], gb.INPUT_HEIGHT)
        self.main_gate.inputs += [node]
        self.draw_node(node)
        self.fond.tag_bind(node.id, "<Button-2>", node.destroy)
        self.clean_select()

    def add_clock_input(self, evt):
        node = Main_input_node(self.main_gate, self)
        node.center = (self.inout_pos[0], gb.INPUT_HEIGHT)
        self.main_gate.inputs += [node]
        self.draw_node(node)
        self.fond.tag_bind(node.id, "<Button-2>", node.destroy)
        self.clean_select()


    ## _________________ OUTPUT _____________________ ##

    def output_select(self, evt):
        x = min(evt.x, gb.WINDOW_WIDTH - 70)
        y = evt.y
        self.inout_pos = (evt.x, evt.y)
        frame_id = self.fond.create_rectangle(x - 3, y - 65, x + 63, y + 3, fill = "lightgray")
        self.inout_frame = (x - 3, y - 65, x + 63, y + 3)
        self.node_select.add(frame_id)

        self.load_node_choice(x, y - 62, "Single", "output")
        self.load_node_choice(x, y - 30, "Count", "output")

    def add_single_output(self, evt):
        if not self.inout_pos[0]:
            self.inout_pos = (evt.x, evt.y)
        node = Main_output_node(self.main_gate, self)
        node.center = (self.inout_pos[0], gb.WINDOW_HEIGHT - gb.OUTPUT_HEIGHT)
        self.main_gate.outputs += [node]
        self.draw_node(node)
        self.fond.tag_bind(node.id, "<Button-2>", node.destroy)
        self.clean_select()

    def add_count_output(self, evt):
        node = Main_output_node(self.main_gate, self)
        node.center = (self.inout_pos[0], gb.WINDOW_HEIGHT - gb.OUTPUT_HEIGHT)
        self.main_gate.outputs += [node]
        self.draw_node(node)
        self.fond.tag_bind(node.id, "<Button-2>", node.destroy)
        self.clean_select()

    ######################### BINDINGS #########################
    def enable_bindings(self):
        gb.debug("Bindings enabled")
        for to_bind in self.bindings:
            self.bind(to_bind, self.bindings[to_bind])
    def disable_bindings(self):
        gb.debug("Bindings disabled")
        for to_unbind in self.bindings:
            self.unbind(to_unbind)

    def save_pressed_key(self, evt):
        if evt.keycode == 22:
            self.gate_name = self.gate_name[:-1]
        elif evt.char.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 ":
            self.gate_name += evt.char.upper()
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
        if self.inout_frame[0]:
            if not (self.inout_frame[0] < evt.x < self.inout_frame[2] and self.inout_frame[1] < evt.y < self.inout_frame[3]):
                self.clean_select()

    ######################### GATE GENERATOR #########################
    def load_below_gates(self):
        for i, gate_name in enumerate(os.listdir("lib/structs/")):
            x = i * 110 + 10 + self.gate_gen_x
            y = 25
            generator = Generator(gate_name, self)
            self.generators.add(generator)
            generator.id = self.fond.create_rectangle(x, y - 20, x + 100, y + 20, width = 2, fill = gb.BOX_BG)
            generator.name_id = self.fond.create_text(x + 50, y, text = gate_name)
            self.fond.tag_bind(generator.id, "<Button-1>", generator.create_gate)
            self.fond.tag_bind(generator.name_id, "<Button-1>", generator.create_gate)
        self.max_gate_gen_x = x

    def reload_below_gate(self):
        for generator in self.generators:
            self.fond.delete(generator.id)
            self.fond.delete(generator.name_id)
        self.load_below_gates()

    def scroll(self, evt):
        if evt.delta != 0: # for windows
            self.gate_gen_x += evt.delta / 30
        if evt.num == 4: # for linux
            self.gate_gen_x += 30
            self.gate_gen_x = min(self.gate_gen_x, 0)
        if evt.num == 5: # for linux
            self.gate_gen_x -= 30
            delta = self.max_gate_gen_x - gb.WINDOW_WIDTH + 100
            if delta < 0:
                self.gate_gen_x += 30
        self.reload_below_gate()

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
        self.order_inputs_outputs()
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
    def get_center_from_point(self, node_or_tuple):
        try:
            return node_or_tuple.center
        except:
            return node_or_tuple

    def draw_link(self, link):
        """
        Dessine un link
        """
        x, y = self.get_center_from_point(link.points_list[-1])
        link.id_list += [self.fond.create_line(x, y, x, y, fill = "white", width = 2)]
        self.fond.tag_bind(link.id_list[-1], "<Button-3>", link.r_clic)

    def draw_node(self, node):
        """
        Dessine une node
        """
        x, y = node.center
        node.id = self.fond.create_oval(x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE, outline = "black", width = 2, fill = "white")
        self.fond.tag_bind(node.id, "<Button-1>", node.clic)
        self.fond.tag_bind(node.id, "<Button-3>", node.r_clic)
        self.fond.tag_bind(node.id, "<Button-2>", node.destroy)
        if gb.DEBUG:
            node.text = self.fond.create_text(x, y, text = str(node.id))
            self.fond.tag_bind(node.text, "<Button-1>", node.clic)
            self.fond.tag_bind(node.text, "<Button-3>", node.r_clic)
            self.fond.tag_bind(node.text, "<Button-2>", node.destroy)
        if node.get_type() not in ("main_input", "main_output"):
            if gb.DEBUG:
                self.fond.tag_bind(node.text, "<Button-1>", node.gate.clic)
            self.fond.tag_bind(node.id, "<Button-1>", node.gate.clic)


    def draw_gate(self, gate):
        """
        Affiche une gate et les nodes associées
        """
        x, y = gate.center
        gate.id = self.fond.create_rectangle(x - gate.width, y - gb.BOX_HEIGHT, x + gate.width, y + gb.BOX_HEIGHT, outline = "black", fill = gb.BOX_BG, width = 3)
        self.fond.tag_bind(gate.id, "<Button-1>", gate.clic)
        self.fond.tag_bind(gate.id, "<Button-2>", gate.delete)
        gate.name_id = self.fond.create_text(x, y, text = gate.name)
        self.fond.tag_bind(gate.name_id, "<Button-1>", gate.clic)
        self.fond.tag_bind(gate.name_id, "<Button-2>", gate.delete)

        for node in gate.inputs:
            self.draw_node(node)
        for node in gate.outputs:
            self.draw_node(node)

    ######################### UPDATE DISPLAY #########################
    def clock_update(self):
        self.update_all()
        self.after(300, self.clock_update)

    def update_all(self):
        """
        Deux update sont nécéssaire pour que les flip flop marchent
        Un update se fait en 3 étapes :
        1) On update les nodes d'entrée, afin de mettre à jour leur date de MAJ
        et mettre à jour l'affichage, meme de celles qui ne sont pas reliées
        2) On update toutes les gates, afin de mettre à jour les gates, meme
        celles qui ne sont pas connectées
        3) On update en partant des nodes de sortie
        """
        gb.PRE_UPDATE()
        # 1)
        for node in self.main_gate.inputs:
            node.need_previous()
        # 2)
        for gate in self.gates:
            for output_node in gate.outputs:
                output_node.need_previous()
        # 3)
        for node in self.main_gate.outputs:
            node.need_previous()
        # Deuxieme update
        gb.UPDATE_ID += 1
        # # 1)
        # for node in self.main_gate.inputs:
        #     node.need_previous()
        # # 2)
        # for gate in self.gates:
        #     for output_node in gate.outputs:
        #         output_node.need_previous()
        # # 3)
        # for node in self.main_gate.outputs:
        #     node.need_previous()

    def update(self, item):
        target_class = item.__class__.__bases__

        if type(item) == Link:
            x2, y2 = self.get_center_from_point(item.points_list[-1])
            x1, y1 = self.get_center_from_point(item.points_list[-2])
            self.fond.coords(item.id_list[-1], x1, y1, x2, y2)
            x2, y2 = self.get_center_from_point(item.points_list[0])
            x1, y1 = self.get_center_from_point(item.points_list[1])
            self.fond.coords(item.id_list[0], x1, y1, x2, y2)

            if item.get_output():
                # Permet d'afficher le lien en rouge lorsque la node d'entrée est active
                item.active = item.get_output().active
            for link_seg_id in item.id_list:
                self.fond.itemconfig(link_seg_id, fill = "red" if item.active else "white")
            self.fond.tag_lower(item.id_list[-1])

        elif type(item) in (Input_node, Output_node, Main_input_node, Main_output_node):
            x, y = item.center
            self.fond.coords(item.id, x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE)
            self.fond.itemconfig(item.id, fill = "red" if item.active else "white")
            if gb.DEBUG:
                self.fond.coords(item.text, x, y)

            # On update les liens avant et après la node
            for link in item.next_links:
                self.update(link)
            if item.prev_link:
                self.update(item.prev_link)

        else:
            if item.name != "MAIN":
                # c'est une gate normale
                x, y = item.center
                dx, dy = item.delta_x, item.delta_y
                self.fond.coords(item.id, x - item.width, y - gb.BOX_HEIGHT, x + item.width, y + gb.BOX_HEIGHT)
                self.fond.coords(item.name_id, x, y)

            for node in item.inputs:
                self.update(node)
            for node in item.outputs:
                self.update(node)

        self.fond.tag_lower(self.real_bg)



def run():
    fen = Window()
