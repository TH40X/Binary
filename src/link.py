import src.node as nd
import src.globals as gb

class Link:
    def __init__(self, node1):
        self.node1 = node1

    def finish(self, node2):
        self.node2 = node2

    def delete(self):
        if type(self.node1) == nd.Input_node or type(self.node1) == nd.Main_output_node:
            # Supprime la node précédente de node1
            self.node1.prev = None
            self.node1.prev_link = None
            # Supprime node1 de la node précédente
            self.node2.next.remove(self.node1)
            if gb.DEBUG:print(self.node2.next_links)
            self.node2.next_links.remove(self)
            # Supprime l'affichage du lien
            self.node1.fen.fond.delete(self.id)
            self.node1.push()
        else:
            self.node1, self.node2 = self.node2, self.node1
            self.delete()
