from src.node import Input_node, Output_node
import src.globals as gb



class Box:
    def __init__(self):
        pass

    def draw(self, fen):
        pass




class Current_box(Box):
    """
    Decrit l'intérieur de la box en construction
    """
    def __init__(self):
        """
        initialise une box vide : pas d'entrées, pas de sorties
        """
        self.inputs = [] # liste des nodes d'entrée
        self.outputs = [] # liste des nodes de sortie

    def update_centers(self, target, fen):
        """
        Change la position des nodes pour l'ajout (change = 1)
        ou la suppression (change = -1) d'une node
        """
        taille = len(target)
        x = 50 * (target is self.inputs) + (gb.WINDOW_WIDTH - 50) * (target is self.outputs)
        for i, node in enumerate(target):
            y = gb.WINDOW_HEIGH / 2 + 100 * i - (taille - 1)  * 50
            node.update_center((x, y), fen)

    def add_input(self, fen):
        """
        Ajoute une entrée : fixe sa valeur à false
        Renvoie la node ajoutée
        """
        node = Input_node((0, 0))
        self.inputs += [node]
        id = node.draw(fen)
        self.update_centers(self.inputs, fen)
        return id

    def remove_input(self, fen):
        """
        retire la dernire entrée saisie
        Renvoie la node supprimée
        """
        if not len(self.inputs):
            return None
        node = self.inputs[-1]
        self.inputs = self.inputs[:-1]
        self.update_centers(self.inputs, fen)
        return node.ident

    def add_output(self, fen):
        """
        Ajoute une sortie
        Renvoie la node ajoutée
        """
        node = Output_node((0, 0))
        self.outputs += [node]
        id = node.draw(fen)
        self.update_centers(self.outputs, fen)
        return id

    def remove_output(self, fen):
        """
        retire la dernire sortie saisie
        Renvoie la node supprimée
        """
        if not len(self.outputs):
            return None
        node = self.outputs[-1]
        self.outputs = self.outputs[:-1]
        self.update_centers(self.outputs, fen)
        return node.ident

    def evaluate(self):
        """
        Calcule la sortie en fonction de l'entrée
        """
        for output_node in self.outputs:
            yield node.evaluate()
