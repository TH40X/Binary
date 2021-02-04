import src.globals as gb


class Gate:
    def __init__(self, inputs, outputs):
        gb.GATE_NUMBER += 1
        self.center = (gb.WINDOW_WIDTH / 2, gb.WINDOW_HEIGHT / 2)
        self.inputs = inputs
        self.outputs = outputs
        self.width = max(len(self.inputs), len(self.outputs)) * (2 * gb.NODE_SIZE) / 2
        self.delta_x, self.delta_y = 0, 0

    def delete(self, evt):
        gb.debug("Suppression de la gate : {}".format(self.id))
        self.fen.gates.remove(self)
        for node in self.inputs + self.outputs:
            node.delete(evt)  # ne détruit que les liens
            self.fen.fond.delete(node.id)
            if gb.DEBUG:
                self.fen.fond.delete(node.text)
        self.fen.fond.delete(self.id)
        self.fen.fond.delete(self.name_id)

    def update_nodes_coords(self):
        y = self.center[1] - gb.BOX_HEIGHT
        for i, node in enumerate(self.inputs):
            x = self.center[0] + (2 * gb.NODE_SIZE) * i - (len(self.inputs) - 1) * (2 * gb.NODE_SIZE) / 2
            node.update_center((x, y))
        y = self.center[1] + gb.BOX_HEIGHT
        for i, node in enumerate(self.outputs):
            x = self.center[0] + (2 * gb.NODE_SIZE) * i - (len(self.outputs) - 1) * (2 * gb.NODE_SIZE) / 2
            node.update_center((x, y))

    def evaluate(self):
        gb.debug("Evaluation initialisée sur la gate {} : {}".format(self.name, self.id))
        """
        ATTENTION : UTILISEE QU'A L'INITIALISATION DE LA GATE
        """
        gb.PRE_UPDATE()
        for output_node in self.outputs:
            output_node.need_previous()

    def clic(self, evt):
        gb.debug("clic on box with id = {}".format(self.id))
        self.fen.selected = self
        self.delta_x, self.delta_y = self.center[0] - evt.x, self.center[1] - evt.y

    def __repr__(self):
        nodes_to_string = ""
        for input_node in self.inputs:
            nodes_to_string += "{},".format(input_node.id)
        nodes_to_string = nodes_to_string[:-1] + ":"
        for output_node in self.outputs:
            nodes_to_string += "{},".format(output_node.id)
        nodes_to_string = nodes_to_string[:-1] + "\n"
        return "Gate:{}:{}".format(self.name, nodes_to_string)


class New_gate(Gate):
    """
    Permet de précharger une gate
    """

    def __init__(self, fen, name):
        self.id = None
        self.fen = fen
        self.name = name


class And_gate(Gate):
    def __init__(self, fen):
        self.fen = fen
        self.center = (gb.WINDOW_WIDTH / 2, gb.WINDOW_HEIGHT / 2)
        self.name = "AND"

    def evaluate(self):
        self.outputs[0].active = self.inputs[0].active and self.inputs[1].active


class Not_gate(Gate):
    def __init__(self, fen):
        self.fen = fen
        self.center = (gb.WINDOW_WIDTH / 2, gb.WINDOW_HEIGHT / 2)
        self.name = "NOT"

    def evaluate(self):
        self.outputs[0].active = not self.inputs[0].active
