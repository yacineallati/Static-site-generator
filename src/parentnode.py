from htmlnode import HTMLNode

class ParentNode(HTMLNode):
    def __init__(self, tag, children):
        super().__init__(tag, None, children, None)

    def to_html(self):
        if self.tag == None:
            raise ValueError("All parents must have a tag")
        elif self.children == None:
            raise ValueError("All parents must have a children")
        
        children = ""
        for child in self.children:
            children += child.to_html()
        return f"<{self.tag}>{children}</{self.tag}>"