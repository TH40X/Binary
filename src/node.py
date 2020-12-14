import src.globals as gb


class Node:
    def __init__(self, center, box):
        self.active = False
        self.last_update = 0
        self.box = box
        self.link = set()
        self.center = center


    def draw(self, fen):
        self.fen = fen
        x, y = self.center
        ident = fen.fond.create_oval(x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE, outline = "black", width = 3, fill = "white")
        self.ident = ident
        return ident

    def update_color(self):
        self.fen.fond.itemconfig(self.ident, fill = "red" if self.active else "white")

    def update_center(self, center):
        self.center = center
        x, y = center
        self.fen.fond.coords(self.ident, x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE)




class Input_node(Node):
    def push(self):
        """
        Si la box auquelle la node appartient est à jour, on push les node de sortie
        """
        for node in self.box.inputs:
            # si toutes les nodes ne sont pas à jour : pas la peine d'update
            if not node.link:
                node.last_update = gb.UPDATE_ID
                continue
            if node.last_update < gb.UPDATE_ID:
                return
        # la box est à jour : on l'update
        self.box.evaluate()
        for output_node in self.box.outputs:
            output_node.push()

class Output_node(Node):
    def push(self):
        """
        Envoie la valeur vers les nodes suivantes
        """
        if not self.link:
            # pas de lien qui part de cette node
            return
        for link in self.link:
            next_node = link.input
            next_node.active = self.active
            next_node.last_update = gb.UPDATE_ID
            next_node.push()

class Main_output_node(Input_node):
    def draw(self, fen):
        self.fen = fen
        x, y = self.center
        ident = fen.fond.create_oval(x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE, outline = "black", width = 3, fill = "white")
        self.ident = ident
        return ident

    def push(self):
        pass

class Main_input_node(Output_node):
    def draw(self, fen):
        self.fen = fen
        x, y = self.center
        ident = fen.fond.create_oval(x - gb.NODE_SIZE, y - gb.NODE_SIZE, x + gb.NODE_SIZE, y + gb.NODE_SIZE, outline = "black", width = 3, fill = "white")
        fen.fond.tag_bind(ident, "<Button-1>", self.clic)
        self.ident = ident
        return ident

    def clic(self, evt):
        print("clic on node with id = {}".format(self.ident))
        self.active = not self.active
        self.update_color()
        self.box.evaluate()
