import src.globals as gb


class Node:
    def __init__(self, center):
        self.link = None
        self.center = center

    def update_center(self, center, fen):
        self.center = center
        x, y = center
        fen.fond.coords(self.ident, x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE)

    def get_link(self):
        return this.link

    def set_link(self, link):
        self.link = link

    def draw(self, fen):
        x, y = self.center
        ident = fen.fond.create_oval(x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE, outline = "black", width = 3, fill = "white")
        fen.fond.tag_bind(ident, "<Button-1>", self.clic)
        self.ident = ident
        return ident

    def clic(self, evt):
        print("clic on node with id = {}".format(self.ident))



class Input_node(Node):
    def get_type(self):
        return "input_node"

class Output_node(Node):
    def get_type(self):
        return "output_node"

    def evaluate(self):
        """
        Evalue la node à True ou False
        """
        link = self.link
        if link is None:
            return False
        else:
            origin = link.get_output()
            return origin.evaluate()
