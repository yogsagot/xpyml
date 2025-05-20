class Node:
    def __init__(self, tag=None, value=None, attributes=None, parent=None):
        self.tag = tag
        self.value = value
        self.attributes = attributes or {}
        self.children = []
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def __str__(self, level=0):
        indent = "  " * level
        result = indent
        if self.tag:
            result += f"<{self.tag}"
            if self.attributes:
                attrs = " ".join(f'{k}="{v}"' for k, v in self.attributes.items())
                result += " " + attrs
            result += ">"
        if self.value:
            result += self.value
        # result += "\n"
        for child in self.children:
            result += child.__str__(level + 1)
        if self.tag:
            result += indent + f"</{self.tag}>"
        return result


class Parser:
    def __init__(self):
        self.root = Node()
        self.current = self.root

    def parse(self, text):
        i = 0
        while i < len(text):
            if text[i] == '<':
                if text[i + 1] == '/':
                    # Closing tag
                    end = text.find('>', i)
                    if end != -1:
                        self.current = self.current.parent
                        i = end + 1
                else:
                    # Opening tag
                    end = text.find('>', i)
                    if end != -1:
                        tag_content = text[i + 1:end]
                        tag_parts = tag_content.split()
                        tag_name = tag_parts[0]

                        # Parse attributes
                        attributes = {}
                        for part in tag_parts[1:]:
                            if '=' in part:
                                key, value = part.split('=', 1)
                                value = value.strip('"\'')
                                attributes[key] = value

                        new_node = Node(tag=tag_name, attributes=attributes)
                        self.current.add_child(new_node)
                        self.current = new_node
                        i = end + 1
            else:
                # Text content
                next_tag = text.find('<', i)
                if next_tag == -1:
                    next_tag = len(text)
                content = text[i:next_tag].strip()
                if content:
                    text_node = Node(value=content)
                    self.current.add_child(text_node)
                i = next_tag

        return self.root
