import src.globals as gb
from src.link import Link


class Node:
    def __init__(self, gate, fen=None):
        gb.NODE_NUMBER += 1
        self.last_update = 0
        self.id = None
        self.fen = fen
        self.active = False
        self.gate = gate
        self.center = (0, 0)
        # self.nodes représente les nodes auquelles elle est connectée
        # pour une input_node, il ne peut y avoir au plus qu'une seule node
        self.prev = None
        self.next_links = set()
        self.prev_link = None

    def destroy(self, evt=None):
        self.delete()

    def is_hidden(self):
        return False

    def get_sub_type(self):
        return "simple"

    def need_previous(self):
        debug(self)
        if self.last_update < gb.UPDATE_ID:
            gb.UPDATE_NUMBER += 1
            self.last_update = gb.UPDATE_ID
            if self.get_type() == "output" and self.gate.name in ("AND", "NOT"):
                for input in self.gate.inputs:
                    input.need_previous()
                self.gate.evaluate()
            elif self.prev:
                self.prev.need_previous()
                self.active = self.prev.active
            else:
                self.active = False
        if not self.is_hidden():
            self.fen.update(self)

    def update_center(self, center):
        self.center = center

    def clic(self, evt):
        """
        Ne fait rien mais doit etre déclaré car utilisé par les main_in/output
        """
        if gb.DEBUG: print("clic on node with id = {}".format(self.id))

    def r_clic(self, evt):
        if gb.DEBUG: print("_____________________________________________")
        self.destroy_old_input()  # détruit les liens arrivant sur la node si c'est un input
        if self.fen.link == None:
            if gb.DEBUG: print("Initialisation d'un lien")
            # Création d'un nouveau lien
            link = Link(self)
            self.fen.draw_link(link)
            self.fen.link = link
        else:
            if (self.fen.link.node1.get_type(), self.get_type()) in (
                    ("input", "output"), ("output", "input"),
                    ("main_input", "input"), ("input", "main_input"),
                    ("main_input", "main_output"), ("main_output", "main_input"),
                    ("output", "main_output"), ("main_output", "output")):
                if gb.DEBUG: print("Terminaison d'un lien")
                # Implémentation du lien
                self.fen.link.finish(self)
                self.link_to()
                self.fen.link = None
                self.fen.update_all()


class Input_node(Node):
    def get_type(self):
        return ("input")

    def link_to(self):
        self.prev = self.fen.link.node1
        self.prev_link = self.fen.link
        self.prev.next_links.add(self.fen.link)
        self.fen.update(self.prev)
        # Après l'ajout d'un lien, on update avec un push
        gb.PRE_UPDATE()
        self.need_previous()
        # self.prev.push()
        self.fen.update(self.gate)

    def destroy_old_input(self):
        """
        Detruit le lien vers la node précédent s'il existe
        """
        self.delete(None)

    def delete(self, evt=None):
        """
        La suppression pour ne node input doit efface tous les liens précédents
        """
        if self.prev_link:
            self.prev_link.delete()

    def __repr__(self):
        if self.prev:
            return ("Node:input:{}:{}\n".format(self.id, self.prev.id))
        else:
            return ("Node:input:{}:0\n".format(self.id))


class Output_node(Node):
    def get_type(self):
        return ("output")

    def link_to(self):
        self.next_links.add(self.fen.link)
        self.fen.link.node1.prev = self
        self.fen.link.node1.prev_link = self.fen.link
        self.fen.update(self)
        # Après l'ajout d'un lien, on update avec un push
        gb.PRE_UPDATE()

    def destroy_old_input(self):
        """
        Pas besoin de détruire le lien dans le cas d'une node output
        """
        pass

    def delete(self, evt=None):
        """
        La suppression pour ne node output doit efface tous les liens suivants
        """
        for link in self.next_links.copy():
            link.delete()

    def __repr__(self):
        return ("Node:output:{}:0\n".format(self.id))


class Hidden_input_node(Input_node):
    def is_hidden(self):
        return True


class Hidden_output_node(Output_node):
    def is_hidden(self):
        return True


class Main_output_node(Input_node):
    def get_type(self):
        return ("main_output")

    def clic(self, evt):
        gb.debug("_____________________________________________")

    def __repr__(self):
        if self.prev:
            return ("Node:main_output:{}:{}\n".format(self.id, self.prev.id))
        else:
            return ("Node:main_output:{}:0\n".format(self.id))

    def destroy(self, evt):
        self.delete()  # ne détruit que les liens
        self.fen.fond.delete(self.id)
        if gb.DEBUG:
            self.fen.fond.delete(self.text)
        self.gate.outputs.pop(self.gate.outputs.index(self))


class Main_input_node(Output_node):
    def need_previous(self):
        self.last_update = gb.UPDATE_ID
        self.fen.update(self)

    def get_type(self):
        return ("main_input")

    def clic(self, evt):
        if gb.DEBUG: print("_____________________________________________")
        if gb.DEBUG: print("clic on node with id = {}".format(self.id))
        self.active = not self.active
        # self.push()
        self.fen.update_all()

    def __repr__(self):
        return ("Node:main_input:{}:0\n".format(self.id))

    def destroy(self, evt):
        self.delete()  # ne détruit que les liens
        self.fen.fond.delete(self.id)
        if gb.DEBUG:
            self.fen.fond.delete(self.text)
        self.gate.inputs.pop(self.gate.inputs.index(self))


class Main_input_count_node(Main_input_node):
    def get_sub_type(self):
        return "count"

    def add_ext_node(self, evt):
        self.fen.fond.delete(self.ext_node_id)
        self.fen.inout_pos = (self.center[0] + 1.7 * gb.NODE_SIZE, self.center[1])
        new_node = self.fen.add_count_input(None)
        new_node.master_node = self.master_node
        self.master_node.node_amount += 1
        self.next_node = new_node
        self.master_node.update_value_display()

    def update_value_display(self):
        # on est forcément sur la node principale en entrant dans cette fonction
        if hasattr(self, "value_text"):
            x, y = self.center
            x += ((self.node_amount - 1) * gb.NODE_SIZE * 1.7) / 2
            self.fen.fond.itemconfig(self.value_text, text=str(self.get_value()))
            self.fen.fond.coords(self.value_text, x, y - gb.NODE_SIZE * 2)
        else:
            x, y = self.center
            self.value_text = self.fen.fond.create_text(x, y - gb.NODE_SIZE * 2, text=str(self.get_value()),
                                                        fill="#ffffff", font=("Arial", 20))

    def get_value(self):
        tmp = self.master_node
        pow = tmp.node_amount - 1
        value = 0
        while tmp:
            value += int(tmp.active) * (2 ** pow)
            pow -= 1
            tmp = tmp.next_node
        return value

    def delete_ext(self, evt):
        self.fen.fond.delete(self.ext_node_id)

    def destroy_count(self, evt):
        self.fen.fond.delete(self.master_node.value_text)
        self.master_node.destroy(None)
        next = self.master_node
        while next.next_node:
            next.next_node.destroy(None)
            next = next.next_node
        self.fen.fond.delete(next.ext_node_id)


class Main_output_count_node(Main_output_node):
    def get_sub_type(self):
        return "count"

    def add_ext_node(self, evt):
        self.fen.fond.delete(self.ext_node_id)
        self.fen.inout_pos = (self.center[0] + 1.7 * gb.NODE_SIZE, self.center[1])
        new_node = self.fen.add_count_output(None)
        new_node.master_node = self.master_node
        self.master_node.node_amount += 1
        self.next_node = new_node
        self.master_node.update_value_display()

    def update_value_display(self):
        # on est forcément sur la node principale en entrant dans cette fonction
        if hasattr(self, "value_text"):
            x, y = self.center
            x += ((self.node_amount - 1) * gb.NODE_SIZE * 1.7) / 2
            self.fen.fond.itemconfig(self.value_text, text=str(self.get_value()))
            self.fen.fond.coords(self.value_text, x, y + gb.NODE_SIZE * 2)
        else:
            x, y = self.center
            self.value_text = self.fen.fond.create_text(x, y + gb.NODE_SIZE * 2, text=str(self.get_value()),
                                                        fill="#ffffff", font=("Arial", 20))

    def get_value(self):
        tmp = self.master_node
        pow = tmp.node_amount - 1
        value = 0
        while tmp:
            value += int(tmp.active) * (2 ** pow)
            pow -= 1
            tmp = tmp.next_node
        return value

    def delete_ext(self, evt):
        self.fen.fond.delete(self.ext_node_id)

    def destroy_count(self, evt):
        self.fen.fond.delete(self.master_node.value_text)
        self.master_node.destroy(None)
        next = self.master_node
        while next.next_node:
            next.next_node.destroy(None)
            next = next.next_node
        self.fen.fond.delete(next.ext_node_id)


class Clock_node(Main_input_node):
    """
    Node de type clock : n'est utile que lors de la création de la gate, elle
    reste une node de type "main_input" pour la sauvegarde de la gate
    """

    def need_previous(self):
        if self.last_update != gb.UPDATE_ID:
            self.last_update = gb.UPDATE_ID
            self.active = not self.active
            self.fen.update(self)


def debug(node):
    gb.debug("[NEED] {} {} {} id = {}".format(node.get_type(), node.gate.name, node.active, node.id))
