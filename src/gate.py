from src.node import Input_node, Output_node, Main_input_node, Main_output_node
import src.globals as gb



class Gate:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.height = max(len(self.inputs), len(self.outputs)) * (2 * gb.NODE_SIZE + 10) / 2


    def update_nodes_coords(self):
        x = self.center[0] - gb.BOX_WIDTH
        for i, node in enumerate(self.inputs):
            y = self.center[1] + (2 * gb.NODE_SIZE + 10) * i - (len(self.inputs) - 1) * (2 * gb.NODE_SIZE + 10) / 2
            node.update_center((x, y))
        x = self.center[0] + gb.BOX_WIDTH
        for i, node in enumerate(self.outputs):
            y = self.center[1] + (gb.NODE_SIZE + 10) * i - (len(self.outputs) - 1) * (gb.NODE_SIZE + 10) / 2
            node.update_center((x, y))


    def evaluate(self):
        """
        Calcule la sortie en fonction de l'entrée
        """
        for input_node in self.inputs:
            input_node.push()

    def clic(self, evt):
        print("clic on box with id = {}".format(self.ident))

class And_gate(Gate):
    def __init__(self, fen, center):
        self.fen = fen
        self.center = center
        self.name = "AND"

        input1 = Input_node((0, 0), self, fen)
        input2 = Input_node((0, 0), self, fen)
        output = Output_node((0, 0), self, fen)

        Gate.__init__(self, [input1, input2], [output])
        self.update_nodes_coords()

    def evaluate(self):
        self.outputs[0].active = self.inputs[0].active and self.inputs[1].active

class Or_gate(Gate):
    def __init__(self, fen, center):
        self.fen = fen
        self.center = center
        self.name = "OR"

        input1 = Input_node((0, 0), self, fen)
        input2 = Input_node((0, 0), self, fen)
        output = Output_node((0, 0), self, fen)

        Box.__init__(self, [input1, input2], [output])

    def evaluate(self):
        self.outputs[0].active = self.inputs[0].active or self.inputs[1].active


class Current_gate(Gate):
    """
    Decrit l'intérieur de la box en construction
    """
    def __init__(self, fen):
        """
        initialise une box vide : pas d'entrées, pas de sorties
        """
        self.fen = fen
        self.inputs = [] # liste des nodes d'entrée
        self.outputs = [] # liste des nodes de sortie

    def update_centers(self, target):
        """
        Change la position des nodes pour l'ajout (change = 1)
        ou la suppression (change = -1) d'une node
        """
        taille = len(target)
        x = 50 * (target is self.inputs) + (gb.WINDOW_WIDTH - 50) * (target is self.outputs)
        for i, node in enumerate(target):
            y = gb.WINDOW_HEIGHT / 2 + 100 * i - (taille - 1)  * 50
            node.update_center((x, y))

    def add_input(self):
        """
        Ajoute une entrée : fixe sa valeur à false
        Renvoie la node ajoutée
        """
        node = Main_input_node((0, 0), self, self.fen)
        self.inputs += [node]
        self.update_centers(self.inputs)
        return node

    def remove_input(self):
        """
        retire la dernire entrée saisie
        Renvoie la node supprimée
        """
        if not self.inputs:
            return None
        node = self.inputs.pop(-1)
        self.update_centers(self.inputs)
        return node

    def add_output(self):
        """
        Ajoute une sortie
        Renvoie la node ajoutée
        """
        node = Main_output_node((0, 0), self, self.fen)
        self.outputs += [node]
        self.update_centers(self.outputs)
        return node

    def remove_output(self):
        """
        retire la dernire sortie saisie
        Renvoie la node supprimée
        """
        if not self.outputs:
            return None
        node = self.outputs.pop(-1)
        self.update_centers(self.outputs)
        return node

    def evaluate(self):
        """
        Calcule la sortie en fonction de l'entrée
        """
        gb.UPDATE_ID += 1

        for output_node in self.inputs:
            output_node.push()
