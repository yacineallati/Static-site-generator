import unittest

from textnode import TextNode, TextType
from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode
from utils import *


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD, "localhost.com")
        node2 = TextNode("This is a text node", TextType.BOLD, "localhost.com")
        node3 = TextNode("this is also a text node", TextType.BOLD, "localhost.com")
        node4 = TextNode("this is also a text node", TextType.TEXT, "localhost.com")
        self.assertEqual(node, node2)
        self.assertNotEqual(node, node3)
        self.assertNotEqual(node, node4)
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node =  HTMLNode("a", "this is a link")
        node2 = HTMLNode(
            "a",
            "this is a link",
            "children",
            {
                "href": "https://www.google.com",
                "target": "_blank",
            }
            )
        node3 = HTMLNode(
            "p",
            "this is a paragraph"
            )

        node2.props_to_html()
        node.props_to_html()
        node3.props_to_html()

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        node2=  LeafNode("b", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
        self.assertEqual(node2.to_html(), "<b>Hello, world!</b>")


class TestLeafNode(unittest.TestCase):    
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

class TestTextSplitting(unittest.TestCase):
    def test_split_nodes_delimiter_basic(self):
        node = TextNode("This is *italic* text", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].text, "This is ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "italic")
        self.assertEqual(nodes[1].text_type, TextType.ITALIC)
        self.assertEqual(nodes[2].text, " text")
        self.assertEqual(nodes[2].text_type, TextType.TEXT)

    def test_split_nodes_delimiter_no_delimiters(self):
        node = TextNode("This is text", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, "This is text")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)

    def test_split_nodes_delimiter_single_delimiter(self):
        node = TextNode("This is *incomplete", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, "This is *incomplete")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes
        )

    def test_markdown_to_blocks(self):
        md = """
    This is **bolded** paragraph

    This is another paragraph with _italic_ text and `code` here
    This is the same paragraph on a new line

    - This is a list
    - with items
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
def test_block_to_block_Types(self):
    md = """
        # Heading 1


        ###### Heading 6


        ####### Invalid heading


        ```Code```


        > Multi-line
        > quote block


        1. First item
        2. Second item
        """

    blocks = markdown_to_blocks(md)
    expected_types = [
        BlockType.HEADING,      # "# Heading 1"
        BlockType.HEADING,      # "###### Heading 6"
        BlockType.PARAGRAPH,    # "####### Invalid heading"
        BlockType.CODE,         # "```Code```"
        BlockType.QUOTE,        # "> Multi-line\n> quote block"
        BlockType.ORDERED_LIST  # "1. First item\n2. Second item"
    ]

    for block, expected_type in zip(blocks, expected_types):
        actual_type = block_to_block_type(block)
        self.assertEqual(
            actual_type,
            expected_type,
            f"Expected {expected_type} for block '{block}', but got {actual_type}"
        )
    
def test_paragraphs(self):
    md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
        html,
        "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
    )

def test_codeblock(self):
    md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
        html,
        "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
    )


if __name__ == "__main__":
    unittest.main()