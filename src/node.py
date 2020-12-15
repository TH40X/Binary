import src.globals as gb
from src.link import Link

class Node:
    def __init__(self, center, gate, fen):
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
        print("clic on node with id = {}".format(self.id))

    def r_clic(self, evt):
        print("_____________________________________________")
        self.destroy_old_input() # détruit les liens arrivant sur la node si c'est un input
        if self.fen.link == None:
            print("Initialisation d'un lien")
            #Création d'un nouveau lien
            link = Link(self)
            id = self.fen.draw_link(link)
            link.id = id
            self.fen.link = link
        else:
            print("Terminaison d'un lien")
            #Implémentation du lien
            self.fen.link.finish(self)
            self.link_to()
            self.fen.link = None





class Input_node(Node):
    def push(self):
        """
        Si la box auquelle la node appartient est à jour, on push les node de sortie
        A la fin du push, on update la node, aisin, les nodes sont update en cascade
        """
        print("push effectué sur la node input : {}".format(self.id))

        if not self.prev:
            self.active = False
        self.gate.evaluate()
        for output_node in self.gate.outputs:
            output_node.push()
        self.fen.update(self)

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

class Output_node(Node):
    def push(self):
        """
        Envoie la valeur vers les nodes suivantes
        """
        print("push effectué sur la node output : {}".format(self.id))
        if not self.next:
            print("pas de lien à exploiter")
            # pas de lien qui part de cette node
        else:
            for node in self.next:
                print(node)
                node.active = self.active
                print(node.active)
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

class Main_output_node(Input_node):
    def push(self):
        """
        Ne doit rien faire, car c'est les nodes de sortie
        """
        self.fen.update(self)
        pass
    def clic(self, evt):
        print("_____________________________________________")
        pass

class Main_input_node(Output_node):

    def clic(self, evt):
        print("_____________________________________________")
        print("clic on node with id = {}".format(self.id))
        self.active = not self.active
        self.push()
