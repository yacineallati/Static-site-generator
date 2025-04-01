import re
from textnode import TextType, TextNode
from leafnode import LeafNode
from parentnode import ParentNode
from enum import Enum


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

    
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    result = []
    for node in old_nodes:
        delimiter_positions = []
        text = node.text
        start = 0
        while True:
            index = text.find(delimiter, start)
            if index == -1:
                break
            delimiter_positions.append(index)
            start = index + len(delimiter)
        
        if len(delimiter_positions) < 2:
            result.append(node)
            continue
            
        result.append(TextNode(text[:delimiter_positions[0]], TextType.TEXT))
        result.append(TextNode(
            text[delimiter_positions[0] + len(delimiter):delimiter_positions[1]], 
            text_type
        ))
        result.append(TextNode(text[delimiter_positions[1] + len(delimiter):], TextType.TEXT))   
    return result


def extract_markdown_images(text):
    images = re.findall(r"!\[(.*?)\]\s*\((.*?)\)", text)
    return images

def extract_markdown_links(text):
    links = re.findall(r"\[(.*?)\]\s*\((.*?)\)", text)
    return links

def split_nodes_image(old_nodes):
    result = []
    for node in old_nodes:
        images = extract_markdown_images(node.text)
        if not images:
            result.append(node)
            continue
        remaining_text = node.text
        for image in images:
            alt, url = image[0], image[1]
            pattern = re.compile(r"!\[" + re.escape(alt) + r"\]\s*\(" + re.escape(url) + r"\)")
            parts = pattern.split(remaining_text, maxsplit=1)
            
            if parts[0]:
                result.append(TextNode(parts[0], TextType.TEXT))
            
            result.append(TextNode(alt, TextType.IMAGE, url))
            
            remaining_text = parts[1] if len(parts) > 1 else ""
            
        if remaining_text:
            result.append(TextNode(remaining_text, TextType.TEXT))
    return result

def split_nodes_link(old_nodes):
    result = []
    for node in old_nodes:
        links = extract_markdown_links(node.text)
        links = [link for link in links if not node.text.startswith('!')]
        if not links:
            result.append(node)
            continue
            
        remaining_text = node.text
        for link in links:
            text, url = link[0], link[1]
            parts = remaining_text.split(f"[{text}]({url})", 1)
            
            if parts[0]:
                result.append(TextNode(parts[0], TextType.TEXT))
            
            result.append(TextNode(text, TextType.LINK, url))
            
            remaining_text = parts[1] if len(parts) > 1 else ""
            
        if remaining_text:
            result.append(TextNode(remaining_text, TextType.TEXT))    
    return result

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    cleaned_blocks = []
    for block in blocks:
        lines = [line.strip() for line in block.split("\n")]
        cleaned_block = "\n".join(line for line in lines if line)
        if cleaned_block:
            cleaned_blocks.append(cleaned_block)
    return cleaned_blocks

def is_block_a_heading(block):
    if block.startswith("#"):
        words = block.split()
        return len(words[0]) <= 6
    return False

def is_block_a_code_snippet(block):
    return block.startswith("```") and block.endswith("```")

def is_block_a_quote(block):
    lines = block.split("\n")
    quote_valid = [line.startswith(">") for line in lines]
    return all(quote_valid)
            
def is_block_an_unordered_list(block):
    lines = block.split("\n")
    unordered_valid = [line.startswith("- ") for line in lines]
    return all(unordered_valid)

def is_block_an_ordered_list(block):
    lines = block.split("\n")
    ordered_valid = [line.startswith(f"{i+1}. ") for i, line in enumerate(lines)]
    return all(ordered_valid)

    
def block_to_block_type(block):
    if is_block_a_heading(block):
        return BlockType.HEADING
    elif is_block_a_code_snippet(block):
        return BlockType.CODE
    elif is_block_an_unordered_list(block):
        return BlockType.UNORDERED_LIST
    elif is_block_an_ordered_list(block):
        return BlockType.ORDERED_LIST
    elif is_block_a_quote(block):
        return BlockType.QUOTE
    else: 
        return BlockType.PARAGRAPH
    
def text_node_to_html(node: TextNode):
    html_map = {
        TextType.TEXT: LeafNode(None, node.text),
        TextType.BOLD: LeafNode("b", node.text),
        TextType.ITALIC: LeafNode("i", node.text),
        TextType.CODE: LeafNode("code", node.text),
        TextType.LINK: LeafNode("a", node.text, f"href={node.url}"),
        TextType.IMAGE: LeafNode("img", "", f"src={node.url} alt={node.text}")
    }
    
    return html_map.get(node.text_type)
    

def heading_block_to_html(block):
    words = block.split()
    heading_marker = words[0]          
    heading_level = len(heading_marker)

    title_text = block[len(heading_marker):].strip()

    nodes = text_to_textnodes(title_text)
    children = []
    for node in nodes:
        html_snippet = text_node_to_html(node)
        children.append(html_snippet)
    return ParentNode(f"h{heading_level}", children)

def code_block_to_html(block):
    nodes = text_to_textnodes(block)
    children = []
    for node in nodes :
        html_snippet = text_node_to_html(node)
        children.append(html_snippet) 
    return ParentNode("pre", [ParentNode("code", children)])

def quote_block_to_html(block):
    lines = block.split("\n")
    children = []
    for line in lines:
        clean_line = re.sub(r'^>\s*', '', line).strip()
        if clean_line:
            nodes = text_to_textnodes(clean_line)
            for node in nodes:
                html_node = text_node_to_html(node)
                if html_node:
                    children.append(html_node)
    return ParentNode("blockquote", children)
    
def ordered_list_block_to_html(block):
    lines = block.split("\n")
    children = []
    for line in lines:
        clean_line = re.sub(r'^\d+\.\s+', '', line)
        nodes = text_to_textnodes(clean_line)
        li_children = []
        for node in nodes:
            li_children.append(text_node_to_html(node))
        children.append(ParentNode("li", li_children))
    return ParentNode("ol", children)

def unordered_list_block_to_html(block):
    lines = block.split("\n")
    children = []
    for line in lines:
        clean_line = line.replace("- ", "", 1)
        nodes = text_to_textnodes(clean_line)
        
        li_children = []
        for node in nodes:
            html_node = text_node_to_html(node)
            if html_node:
                li_children.append(html_node)
                
        li_element = ParentNode("li", li_children)
        children.append(li_element)
        
    return ParentNode("ul", children)

def paragraph_block_to_html(block):
    nodes = text_to_textnodes(block)
    children = []
    for node in nodes :
        html_snippet = text_node_to_html(node)
        children.append(html_snippet)
    return ParentNode("p", children)

def block_to_html(block, block_type):
    block_map = {
        BlockType.HEADING: heading_block_to_html,
        BlockType.UNORDERED_LIST: unordered_list_block_to_html,
        BlockType.ORDERED_LIST: ordered_list_block_to_html,
        BlockType.CODE: code_block_to_html,
        BlockType.QUOTE: quote_block_to_html,
        BlockType.PARAGRAPH: paragraph_block_to_html
    }
    convert_func = block_map.get(block_type)
    if convert_func:
        return convert_func(block)
    return None

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        html_node = block_to_html(block, block_type)
        if html_node:
            children.append(html_node)
    return ParentNode("div", children).to_html()

def extract_title(markdown):        
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            words = block.split()
            if len(words[0]) == 1:
                title_text = block[1:].strip()
                nodes = text_to_textnodes(title_text)
                for node in nodes:
                    html_node = text_node_to_html(node)
                    if html_node:
                        return html_node.to_html()
                
            
    raise Exception("No Title were found")

