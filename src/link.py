import src.node as nd
import src.globals as gb


class Link:
    def __init__(self, node1):
        self.id_list = []
        self.node1 = node1
        self.points_list = [node1, node1]
        self.active = False
        self.node2 = None

    def finish(self, node2):
        self.node2 = node2
        self.points_list[-1] = node2

    def delete_aff(self):
        for link_id in self.id_list:
            self.node1.fen.fond.delete(link_id)

    def delete(self):
        if gb.DEBUG:
            print("Suppression d'un lien\n___________________________________")
        if type(self.node1) == nd.Input_node or type(self.node1) == nd.Main_output_node or type(
                self.node1) == nd.Main_output_count_node:
            # Supprime la node précédente de node1
            self.node1.prev = None
            self.node1.prev_link = None
            # Supprime node1 de la node précédente
            self.node2.next_links.remove(self)
            # Supprime l'affichage du lien
            self.delete_aff()
            self.node1.fen.update_all()
        else:
            self.node1, self.node2 = self.node2, self.node1
            self.delete()

    def get_output(self):
        if type(self.node1) == nd.Output_node or type(self.node1) == nd.Main_input_node or type(
                self.node1) == nd.Clock_node or type(self.node1) == nd.Main_input_count_node:
            return self.node1
        else:
            return self.node2

    def r_clic(self, evt):
        self.points_list.append(self.points_list[-1])
        self.node1.fen.draw_link(self)
