import src.globals as gb
from src.gate import New_gate, Gate, And_gate, Not_gate
from src.node import Input_node, Output_node, Hidden_input_node, Hidden_output_node

def gate_from_name(name, fen):
    if gb.DEBUG:print("Création d'une SOUS gate {}".format(name))
    with open("lib/structs/" + name, "r") as f:
        data = f.readlines()

    final_gate = New_gate(fen, (0, 0), name)
    final_inputs, final_outputs = [], []

    nodes = dict()
    for line in data:
        #Création de la table de relation id : node
        element, name, infos1, infos2 = line.split(":")
        if element == "Gate":
            # on créer une gate
            if name == "AND":
                gate = And_gate(fen, (0, 0))
                input1 = Hidden_input_node((0, 0), gate, fen)
                input2 = Hidden_input_node((0, 0), gate, fen)
                id1, id2 = infos1.split(",")
                nodes[int(id1)] = input1
                nodes[int(id2)] = input2
                output = Hidden_output_node((0, 0), gate, fen)
                nodes[int(infos2)] = output
                Gate.__init__(gate, [input1, input2], [output])
                if gb.DEBUG:print("Création d'une gate AND : {}".format(gate))
            elif name == "NOT":
                gate = Not_gate(fen, (0, 0))
                input = Hidden_input_node((0, 0), gate, fen)
                nodes[int(infos1)] = input
                output = Hidden_output_node((0, 0), gate, fen)
                nodes[int(infos2)] = output
                Gate.__init__(gate, [input], [output])
                if gb.DEBUG:print("Création d'une gate NOT : {}".format(gate))
            else:
                gate = gate_from_name(name, fen)
                # on génère les nodes associées
                inputs, outputs = [], []
                for input_str, already_created in zip(infos1.split(","), gate.inputs):
                    # on fusionne les inputs créés avec ceux de cette gate
                    already_created.id = int(input_str)
                    nodes[already_created.id] = already_created
                    inputs += [already_created]
                for output_str, already_created in zip(infos2.split(","), gate.outputs):
                    already_created.id = int(output_str)
                    nodes[already_created.id] = already_created
                    outputs += [already_created]
                Gate.__init__(gate, inputs, outputs)


        elif element == "Node":
            # si c'est une node "main", on la crée
            if name == "main_input":
                node = Hidden_input_node((0, 0), final_gate, fen)
                nodes[int(infos1)] = node
                final_inputs += [node]
            elif name == "main_output":
                node = Hidden_output_node((0, 0), final_gate, fen)
                nodes[int(infos1)] = node
                final_outputs += [node]

    for line in data:
        # on créer les liens entre chaque node
        element, name, id, target = line.split(":")
        if element == "Node":
            node = nodes[int(id)]
            for other_id in target.split(","):
                other_node = nodes[int(other_id)]
                if name in ("input", "main_output"):
                    node.prev = other_node
                elif name in ("output", "main_input"):
                    if gb.DEBUG:print("SOUS output_node {} reliée vers la node {}".format(id, other_id))
                    node.next.add(other_node)

    Gate.__init__(final_gate, final_inputs, final_outputs)
    return final_gate



def gate_from_add(fen):
    gate = And_gate(fen, (gb.WINDOW_WIDTH / 2, gb.WINDOW_HEIGHT / 2))
    input1 = Input_node((0, 0), gate, fen)
    input2 = Input_node((0, 0), gate, fen)
    output = Output_node((0, 0), gate, fen)
    Gate.__init__(gate, [input1, input2], [output])
    gate.update_nodes_coords()

    fen.gates.add(gate)
    id = fen.draw_gate(gate)
    fen.update_all()

def gate_from_not(fen):
    gate = Not_gate(fen, (gb.WINDOW_WIDTH / 2, gb.WINDOW_HEIGHT / 2))
    input = Input_node((0, 0), gate, fen)
    output = Output_node((0, 0), gate, fen)
    Gate.__init__(gate, [input], [output])
    gate.update_nodes_coords()

    fen.gates.add(gate)
    id = fen.draw_gate(gate)
    fen.update_all()

class Generator:
    def __init__(self, gate_name, fen):
        self.fen = fen
        self.gate_name = gate_name

    def create_gate(self, evt):
        if gb.DEBUG:print("Création d'une Gate {}".format(self.gate_name))
        if self.gate_name == "AND":
            gate_from_add(self.fen)
            return
        if self.gate_name == "NOT":
            gate_from_not(self.fen)
            return

        with open("lib/structs/" + self.gate_name, "r") as f:
            data = f.readlines()

        final_gate = New_gate(self.fen, (gb.WINDOW_WIDTH / 2, gb.WINDOW_HEIGHT / 2), self.gate_name)
        final_inputs, final_outputs = [], []

        nodes = dict()
        for line in data:
            #Création de la table de relation id : node
            element, name, infos1, infos2 = line.split(":")
            if element == "Gate":
                # on créer une gate
                if name == "AND":
                    gate = And_gate(self, (0, 0))
                    input1 = Hidden_input_node((0, 0), gate, self.fen)
                    input2 = Hidden_input_node((0, 0), gate, self.fen)
                    id1, id2 = infos1.split(",")
                    nodes[int(id1)] = input1
                    nodes[int(id2)] = input2
                    output = Hidden_output_node((0, 0), gate, self.fen)
                    nodes[int(infos2)] = output
                    Gate.__init__(gate, [input1, input2], [output])
                elif name == "NOT":
                    gate = Not_gate(self, (0, 0))
                    input = Hidden_input_node((0, 0), gate, self.fen)
                    nodes[int(infos1)] = input
                    output = Hidden_output_node((0, 0), gate, self.fen)
                    nodes[int(infos2)] = output
                    Gate.__init__(gate, [input], [output])
                else:
                    gate = gate_from_name(name, self.fen)
                    # on génère les nodes associées
                    inputs, outputs = [], []
                    for input_str, already_created in zip(infos1.split(","), gate.inputs):
                        # on fusionne les inputs créés avec ceux de cette gate
                        already_created.id = int(input_str)
                        nodes[already_created.id] = already_created
                        inputs += [already_created]
                    for output_str, already_created in zip(infos2.split(","), gate.outputs):
                        already_created.id = int(output_str)
                        nodes[already_created.id] = already_created
                        outputs += [already_created]
                    Gate.__init__(gate, inputs, outputs)


            elif element == "Node":
                # si c'est une node "main", on la crée
                if name == "main_input":
                    node = Input_node((0, 0), final_gate, self.fen)
                    nodes[int(infos1)] = node
                    final_inputs += [node]
                elif name == "main_output":
                    node = Output_node((0, 0), final_gate, self.fen)
                    nodes[int(infos1)] = node
                    final_outputs += [node]

        for line in data:
            # on créer les liens entre chaque node
            element, name, id, target = line.split(":")
            if element == "Node":
                node = nodes[int(id)]
                for other_id in target.split(","):
                    other_node = nodes[int(other_id)]
                    if name in ("input", "main_output"):
                        node.prev = other_node
                    elif name in ("output", "main_input"):
                        if gb.DEBUG:print("output_node {} reliée vers la node {}".format(id, other_id))
                        node.next.add(other_node)

        if gb.DEBUG:print(final_inputs[0].next)
        if gb.DEBUG:print(final_inputs[1].next)
        Gate.__init__(final_gate, final_inputs, final_outputs)
        final_gate.update_nodes_coords()
        self.fen.gates.add(final_gate)
        id = self.fen.draw_gate(final_gate)
        final_gate.id = id
        if gb.DEBUG:print("création de la gate : {}".format(id))
        final_gate.evaluate()
        # self.fen.update(final_gate)
