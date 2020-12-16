import src.globals as gb
from src.link import Link
import src.gate as gt

class Node:
    def __init__(self, center, gate, fen=None):
        self.id = None
        self.fen = fen
        self.active = False
        self.gate = gate
        self.center = center
        # self.nodes représente les nodes auquelles elle est connectée
        # pour une input_node, il ne peut y avoir au plus qu'une seule node
        self.next = set()
        self.prev = None
        self.next_links = set()
        self.prev_link = None

    def update_center(self, center):
        self.center = center

    def clic(self, evt):
        if gb.DEBUG:print("clic on node with id = {}".format(self.id))

    def r_clic(self, evt):
        if gb.DEBUG:print("_____________________________________________")
        self.destroy_old_input() # détruit les liens arrivant sur la node si c'est un input
        if self.fen.link == None:
            if gb.DEBUG:print("Initialisation d'un lien")
            #Création d'un nouveau lien
            link = Link(self)
            id = self.fen.draw_link(link)
            link.id = id
            self.fen.link = link
        else:
            if (self.fen.link.node1.get_type(), self.get_type()) in (("input", "output"), ("output", "input")):
                if gb.DEBUG:print("Terminaison d'un lien")
                #Implémentation du lien
                self.fen.link.finish(self)
                self.link_to()
                self.fen.link = None

class Input_node(Node):
    def get_type(self):
        return("input")

    def push(self):
        """
        Si la box auquelle la node appartient est à jour, on push les node de sortie
        A la fin du push, on update la node, ainsi, les nodes sont update en cascade
        """
        debug(self)  

        if type(self.gate) in (gt.And_gate, gt.Not_gate):
            self.gate.evaluate()
            for node in self.gate.outputs:
                node.push()
            return

        if not self.prev:
            self.active = False
        if not self.next:
            if gb.DEBUG:print("pas de lien à exploiter")
        else:
            for node in self.next:
                node.active = self.active
                node.push()
        self.fen.update(self)

    # def push_forward(self):
    #     """
    #     Envoie la valeur vers les nodes suivantes
    #     """
    #     if gb.DEBUG:print("push FORWARD effectué sur la node input : {}".format(self.id))
    #     if not self.next:
    #         if gb.DEBUG:print("pas de lien à exploiter")
    #         # pas de lien qui part de cette node
    #     else:
    #         for node in self.next:
    #             node.active = self.active
    #             node.push()

    def link_to(self):
        self.prev = self.fen.link.node1
        self.prev_link = self.fen.link
        self.prev.next.add(self)
        self.prev.next_links.add(self.fen.link)
        self.fen.update(self.prev)
        #Après l'ajout d'un lien, on update avec un push
        self.prev.push()
        self.fen.update(self.gate)

    def destroy_old_input(self):
        """
        Detruit le lien vers la node précédent s'il existe
        """
        self.delete(None)

    def delete(self, evt):
        """
        La suppression pour ne node input doit efface tous les liens précédents
        """
        if self.prev_link:
            self.prev_link.delete()

    def __repr__(self):
        if self.prev:
            return("Node:input:{}:{}\n".format(self.id, self.prev.id))
        else:
            return("Node:input:{}:\n".format(self.id))

class Output_node(Node):
    def get_type(self):
        return("output")

    def push(self):
        """
        Envoie la valeur vers les nodes suivantes
        """
        debug(self)
        if not self.next:
            if gb.DEBUG:print("pas de lien à exploiter")
            # pas de lien qui part de cette node
        else:
            for node in self.next:
                node.active = self.active
                node.push()
        #fin du push, on update l'affichage
        self.fen.update(self)

    def link_to(self):
        self.next.add(self.fen.link.node1)
        self.next_links.add(self.fen.link)
        self.fen.link.node1.prev = self
        self.fen.link.node1.prev_link = self.fen.link
        self.fen.update(self)
        #Après l'ajout d'un lien, on update avec un push
        self.push()

    def destroy_old_input(self):
        """
        Pas besoin de détruire le lien dans le cas d'une node output
        """
        pass

    def delete(self, evt):
        """
        La suppression pour ne node output doit efface tous les liens suivants
        """
        for link in self.next_links.copy():
            link.delete()

    def __repr__(self):
        next_to_string = ""
        for next in self.next:
            next_to_string += "{},".format(next.id)
        next_to_string = next_to_string[:-1]
        return("Node:output:{}:{}\n".format(self.id, next_to_string))

class Hidden_input_node(Input_node):
    def push(self):
        """
        Push une node : ne fait pas d'update d'affichage
        """
        debug(self)
        if type(self.gate) in (gt.And_gate, gt.Not_gate):
            self.gate.evaluate()
            for node in self.gate.outputs:
                node.push()
            return

        if not self.prev:
            self.active = False
        if not self.next:
            if gb.DEBUG:print("pas de lien à exploiter")
        else:
            for node in self.next:
                node.active = self.active
                node.push()

class Hidden_output_node(Output_node):
    def push(self):
        """
        Push une node : ne fait pas d'update d'affichage
        """
        debug(self)
        if self.next:
            for node in self.next:
                node.active = self.active
                node.push()

class Main_output_node(Input_node):
    def push(self):
        """
        Ne doit rien faire, car c'est les nodes de sortie
        """
        debug(self)
        self.fen.update(self)
        pass
    def clic(self, evt):
        if gb.DEBUG:print("_____________________________________________")
        pass

    def __repr__(self):
        return("Node:main_output:{}:{}\n".format(self.id, self.prev.id))

class Main_input_node(Output_node):
    def clic(self, evt):
        if gb.DEBUG:print("_____________________________________________")
        if gb.DEBUG:print("clic on node with id = {}".format(self.id))
        self.active = not self.active
        self.push()

    def __repr__(self):
        next_to_string = ""
        for next in self.next:
            next_to_string += "{},".format(next.id)
        next_to_string = next_to_string[:-1]
        return("Node:main_input:{}:{}\n".format(self.id, next_to_string))

def debug(node):
        if gb.DEBUG:print("push effectué sur la node de type {}, sur la gate {}, avec pour état {}, et pour id {}".format(node.get_type(), node.gate.name, node.active, node.id))
