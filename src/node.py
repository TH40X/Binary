import src.globals as gb


class Node:
    def __init__(self, center, gate, fen):
        self.fen = fen
        self.active = False
        self.last_update = 0
        self.gate = gate
        self.center = center
        # self.nodes représente les nodes auquelles elle est connectée
        # pour une input_node, il ne peut y avoir au plus qu'une seule node
        self.next = set()
        self.prev = None
        self.links = set()

    def update_center(self, center):
        self.center = center

    def clic(self, evt):
        print("clic on node with id = {}".format(self.id))

    def r_clic(self, evt):
        print(self.fen.link_id)
        if self.fen.link_id == None:
            print("Initialisation d'un lien")
            #Création d'un nouveau lien
            X, Y = self.center
            id = self.fen.fond.create_line(X, Y, X, Y, width = 2, fill = "black")
            self.fen.link_id = id
            self.fen.link_node = self
        else:
            print("Terminaison d'un lien")
            #Implémentation du lien
            x, y = self.fen.link_node.center
            print("lien", self.center[0])
            self.fen.fond.coords(self.fen.link_id, x, y, self.center[0], self.center[1])
            self.link_to(self.fen.link_node)




class Input_node(Node):
    def push(self):
        """
        Si la box auquelle la node appartient est à jour, on push les node de sortie
        """
        for node in self.gate.inputs:
            # si toutes les nodes ne sont pas à jour : pas la peine d'update
            if not node.next:
                # la node n'est pas connectée
                node.last_update = gb.UPDATE_ID
                continue
            if node.last_update < gb.UPDATE_ID:
                return
        # la box est à jour : on l'update
        self.gate.evaluate()
        for output_node in self.gate.outputs:
            output_node.push()

    def link_to(self, other):
        self.prev = other
        self.fen.link_id = None
        self.fen.link_node = None

class Output_node(Node):
    def push(self):
        """
        Envoie la valeur vers les nodes suivantes
        """
        if not self.next:
            # pas de lien qui part de cette node
            return
        for node in self.next:
            node.active = self.active
            node.last_update = gb.UPDATE_ID
            node.push()

    def link_to(self, other):
        self.next.add(other)
        self.links.add(self.fen.link_id)
        self.fen.link_id = None
        self.fen.link_node = None

class Main_output_node(Input_node):
    def clic(self, evt):
        pass

class Main_input_node(Output_node):

    def clic(self, evt):
        print("clic on node with id = {}".format(self.id))
        self.active = not self.active
        self.gate.evaluate()
        self.gate.fen.update(self) # force l'actualisation de la node
