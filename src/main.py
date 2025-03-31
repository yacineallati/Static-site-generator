import os
import shutil
from utils import *

def main():
    public_path = "./public"
    static_path = "./static"
    content_path = "./content"
    template_path = "./template.html"
    if os.path.exists(public_path):
        list = os.listdir(public_path)
        for file in list:
             path = os.path.join(public_path, file)
             if os.path.isfile(path):
                 os.remove(path)
        copy_files(static_path, public_path)
        generate_page(content_path, template_path, public_path)
    else: 
        os.mkdir(public_path)
        copy_files(static_path, public_path)
        generate_page(content_path, template_path, public_path)


        
def copy_files(source_path, dest_path):
    items = os.listdir(source_path)
    for item in items:
        source_item_path = os.path.join(source_path, item)
        dest_item_path = os.path.join(dest_path, item)
        
        if os.path.isfile(source_item_path):
            shutil.copy2(source_item_path, dest_item_path)
        else:
            if not os.path.exists(dest_item_path):
                os.makedirs(dest_item_path)
            copy_files(source_item_path, dest_item_path)


def generate_page(src_path, template_path, dest_path):
    print(f"Generating page from {src_path} to {dest_path} using {template_path}")
    items = os.listdir(src_path)
    for item in items:
        source_item_path = os.path.join(src_path, item)
        # If it's a file, process it
        if os.path.isfile(source_item_path):
            filename, ext = os.path.splitext(item)
            # If it's a markdown file, convert it to HTML
            if ext.lower() in ['.md', '.markdown']:
                with open(source_item_path, 'r', encoding='utf-8') as file:
                    markdown_content = file.read()
                with open(template_path, 'r', encoding='utf-8') as file:
                    template_content = file.read()

                title = extract_title(markdown_content)
                body = markdown_to_html_node(markdown_content)
                template_content = template_content.replace("{{ Title }}", title)
                template_content = template_content.replace("{{ Content }}", body)
                
                # Set the output file in dest_path using the html filename
                output_file = os.path.join(dest_path, f"{filename}.html")
                os.makedirs(dest_path, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(template_content)
            else:
                # For non-markdown files, simply copy them
                os.makedirs(dest_path, exist_ok=True)
                shutil.copy2(source_item_path, os.path.join(dest_path, item))
        else:
            # If it's a directory, create the corresponding directory in dest_path and process recursively
            new_dest_path = os.path.join(dest_path, item)
            os.makedirs(new_dest_path, exist_ok=True)
            generate_page(source_item_path, template_path, new_dest_path)

if __name__ == "__main__":
    main()