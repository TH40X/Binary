import src.globals as gb
from src.link import Link
import src.gate as gt

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

    def destroy(self, evt = None):
        self.delete()

    def is_hidden(self):
        return False

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
        if gb.DEBUG:print("clic on node with id = {}".format(self.id))

    def r_clic(self, evt):
        if gb.DEBUG:print("_____________________________________________")
        self.destroy_old_input() # détruit les liens arrivant sur la node si c'est un input
        if self.fen.link == None:
            if gb.DEBUG:print("Initialisation d'un lien")
            #Création d'un nouveau lien
            link = Link(self)
            self.fen.draw_link(link)
            self.fen.link = link
        else:
            if (self.fen.link.node1.get_type(), self.get_type()) in (
                    ("input", "output"), ("output", "input"),
                    ("main_input", "input"), ("input", "main_input"),
                    ("main_input", "main_output"), ("main_output", "main_input"),
                    ("output", "main_output"), ("main_output", "output")):
                if gb.DEBUG:print("Terminaison d'un lien")
                #Implémentation du lien
                self.fen.link.finish(self)
                self.link_to()
                self.fen.link = None
                self.fen.update_all()

class Input_node(Node):
    def get_type(self):
        return("input")

    def link_to(self):
        self.prev = self.fen.link.node1
        self.prev_link = self.fen.link
        self.prev.next_links.add(self.fen.link)
        self.fen.update(self.prev)
        #Après l'ajout d'un lien, on update avec un push
        gb.PRE_UPDATE()
        self.need_previous()
        # self.prev.push()
        self.fen.update(self.gate)

    def destroy_old_input(self):
        """
        Detruit le lien vers la node précédent s'il existe
        """
        self.delete(None)

    def delete(self, evt = None):
        """
        La suppression pour ne node input doit efface tous les liens précédents
        """
        if self.prev_link:
            self.prev_link.delete()

    def __repr__(self):
        if self.prev:
            return("Node:input:{}:{}\n".format(self.id, self.prev.id))
        else:
            return("Node:input:{}:0\n".format(self.id))

class Output_node(Node):
    def get_type(self):
        return("output")

    def link_to(self):
        self.next_links.add(self.fen.link)
        self.fen.link.node1.prev = self
        self.fen.link.node1.prev_link = self.fen.link
        self.fen.update(self)
        #Après l'ajout d'un lien, on update avec un push
        gb.PRE_UPDATE()

    def destroy_old_input(self):
        """
        Pas besoin de détruire le lien dans le cas d'une node output
        """
        pass

    def delete(self, evt = None):
        """
        La suppression pour ne node output doit efface tous les liens suivants
        """
        for link in self.next_links.copy():
            link.delete()

    def __repr__(self):
        return("Node:output:{}:0\n".format(self.id))

class Hidden_input_node(Input_node):
    def is_hidden(self):
        return True

class Hidden_output_node(Output_node):
    def is_hidden(self):
        return True

class Main_output_node(Input_node):
    def get_type(self):
        return("main_output")
    def clic(self, evt):
        gb.debug("_____________________________________________")

    def __repr__(self):
        if self.prev:
            return("Node:main_output:{}:{}\n".format(self.id, self.prev.id))
        else:
            return("Node:main_output:{}:0\n".format(self.id))

    def destroy(self, evt):
        self.delete() # ne détruit que les liens
        self.fen.fond.delete(self.id)
        self.fen.fond.delete(self.text)
        self.gate.outputs.pop(self.gate.outputs.index(self))

class Main_input_node(Output_node):
    def need_previous(self):
        self.last_update = gb.UPDATE_ID
        self.fen.update(self)
    def get_type(self):
        return("main_input")
    def clic(self, evt):
        if gb.DEBUG:print("_____________________________________________")
        if gb.DEBUG:print("clic on node with id = {}".format(self.id))
        self.active = not self.active
        # self.push()
        self.fen.update_all()

    def __repr__(self):
        return("Node:main_input:{}:0\n".format(self.id))

    def destroy(self, evt):
        self.delete() # ne détruit que les liens
        self.fen.fond.delete(self.id)
        self.fen.fond.delete(self.text)
        self.gate.inputs.pop(self.gate.inputs.index(self))

def debug(node):
    gb.debug("[NEED] {} {} {} id = {}".format(node.get_type(), node.gate.name, node.active, node.id))
