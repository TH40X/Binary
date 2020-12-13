



class Link:
    """
    Décrit un lient entre deux nodes
    """
    def __init__(self, node):
        if node.get_type() == "input_node":
            self.input = node
        else : self.output = node

    def add_node(self, node):
        if node.get_type() == "input_node":
            self.output = node
        else : self.input = node

    def get_input(self):
        return self.output

    def get_output(self):
        return self.input

    def draw(self, fen):
        pass
