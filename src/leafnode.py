from htmlnode import HTMLNode


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props = None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value == None:
            raise ValueError("All leafs must have values")
        if self.tag == None:
            return f"{self.value}"
        if self.tag == "img":
            return f"<{self.tag} {self.props}>"
        if self.tag == "a":
            return f"<{self.tag} {self.props}>{self.value}</{self.tag}>"
        else:
            return f"<{self.tag}>{self.value}</{self.tag}>"
