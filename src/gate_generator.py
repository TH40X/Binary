import src.globals as gb
from src.gate import New_gate, Gate, And_gate, Not_gate
from src.node import Input_node, Output_node, Hidden_input_node, Hidden_output_node


def load_hidden_gate_from_line(nodes, line, fen):
    element, name, infos1, infos2 = line.split(":")
    if name == "AND":
        gate = And_gate(fen)
        input1 = Hidden_input_node(gate, fen)
        input2 = Hidden_input_node(gate, fen)
        id1, id2 = infos1.split(",")
        nodes[int(id1)] = input1
        nodes[int(id2)] = input2
        output = Hidden_output_node(gate, fen)
        nodes[int(infos2)] = output
        Gate.__init__(gate, [input1, input2], [output])
    elif name == "NOT":
        gate = Not_gate(fen)
        input = Hidden_input_node(gate, fen)
        nodes[int(infos1)] = input
        output = Hidden_output_node(gate, fen)
        nodes[int(infos2)] = output
        Gate.__init__(gate, [input], [output])
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


def gate_from_name(name, fen):
    gb.debug("Création d'une SOUS gate {}".format(name))
    with open("lib/structs/" + name, "r") as f:
        data = f.readlines()

    final_gate = New_gate(fen, name)
    final_inputs, final_outputs = [], []

    nodes = dict()
    for line in data:
        # Création de la table de relation id : node
        element, name, infos1, infos2 = line.split(":")
        if element == "Gate":
            load_hidden_gate_from_line(nodes, line, fen)
        elif element == "Node":
            # si c'est une node "main", on la crée
            if name == "main_input":
                node = Hidden_input_node(final_gate, fen)
                nodes[int(infos1)] = node
                final_inputs += [node]
            elif name == "main_output":
                node = Hidden_output_node(final_gate, fen)
                nodes[int(infos1)] = node
                final_outputs += [node]

    update_links(data, nodes)

    Gate.__init__(final_gate, final_inputs, final_outputs)
    return final_gate


def update_links(data, nodes):
    for line in data:
        # on créer les liens entre chaque node
        element, name, id, target = line.split(":")
        if element == "Node":
            node = nodes[int(id)]
            for other_id in target.split(","):
                if int(other_id):
                    other_node = nodes[int(other_id)]
                    if name in ("input", "main_output"):
                        node.prev = other_node


def gate_from_and(fen):
    """
    Créer une gate AND simple
    """
    gate = And_gate(fen)
    input1 = Input_node(gate, fen)
    input2 = Input_node(gate, fen)
    output = Output_node(gate, fen)
    Gate.__init__(gate, [input1, input2], [output])
    update_gate_aff(fen, gate)


def gate_from_not(fen):
    """
    Créer une gate NOT simple
    """
    gate = Not_gate(fen)
    input = Input_node(gate, fen)
    output = Output_node(gate, fen)
    Gate.__init__(gate, [input], [output])
    update_gate_aff(fen, gate)


def update_gate_aff(fen, gate):
    gate.update_nodes_coords()
    fen.gates.add(gate)
    fen.draw_gate(gate)
    fen.update_all()


class Generator:
    def __init__(self, gate_name, fen):
        self.fen = fen
        self.gate_name = gate_name

    def create_gate(self, evt):
        gb.debug("Création d'une Gate {}".format(self.gate_name))
        if self.gate_name == "AND":
            gate_from_and(self.fen)
            return
        if self.gate_name == "NOT":
            gate_from_not(self.fen)
            return

        with open("lib/structs/" + self.gate_name, "r") as f:
            data = f.readlines()

        final_gate = New_gate(self.fen, self.gate_name)
        final_inputs, final_outputs = [], []

        nodes = dict()
        for line in data:
            # Création de la table de relation id : node
            element, name, infos1, infos2 = line.split(":")
            if element == "Gate":
                load_hidden_gate_from_line(nodes, line, self.fen)

            elif element == "Node":
                # si c'est une node "main", on la crée
                if name == "main_input":
                    node = Input_node(final_gate, self.fen)
                    nodes[int(infos1)] = node
                    final_inputs += [node]
                elif name == "main_output":
                    node = Output_node(final_gate, self.fen)
                    nodes[int(infos1)] = node
                    final_outputs += [node]

        update_links(data, nodes)

        Gate.__init__(final_gate, final_inputs, final_outputs)
        update_gate_aff(self.fen, final_gate)
