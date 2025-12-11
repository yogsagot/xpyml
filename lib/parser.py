from lark import Lark, Transformer, v_args, Token


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
            # Python blocks are stored with a special tag for clarity
            if self.tag == "python":
                result += f"{{ {self.value} }}"
            else:
                result += f"<{self.tag}"
                if self.attributes:
                    attrs = " ".join(f'{k}="{v}"' for k, v in self.attributes.items())
                    result += " " + attrs
                result += ">"
        elif self.value:
            result += self.value.strip()

        if self.children:
            result += "\n"
            for child in self.children:
                result += child.__str__(level + 1)
            if self.tag and self.tag != "python":
                result += indent + f"</{self.tag}>"
        elif self.tag and self.tag != "python":
            result += f"</{self.tag}>"

        return result


# Lark Grammar for HTML + Python Semantics
grammar = r"""
    start: node*

    ?node: element
         | text
         | python_block

    element: "<" CNAME attributes ">" node* "</" CNAME ">" -> tag
           | "<" CNAME attributes "/>"                     -> self_closing_tag

    attributes: attribute*

    attribute: CNAME ("=" value)?

    ?value: STRING           -> string_value
          | python_block     -> python_value

    // Matches { code } blocks. 
    // Note: This is a simple regex; it doesn't handle nested braces.
    python_block: "{" /[^}]+/ "}"

    // Matches text content, avoiding < (tag start) and { (python start)
    text: /[^<{}]+/

    %import common.CNAME
    %import common.ESCAPED_STRING -> STRING
    %import common.WS
    %ignore WS
"""


class XpymlTransformer(Transformer):
    def start(self, items):
        # Create a virtual root to hold top-level elements
        root = Node(tag="root")
        for item in items:
            root.add_child(item)
        return root

    def tag(self, items):
        tag_name = items[0]
        attrs = items[1]
        children = items[2:-1]
        end_tag_name = items[-1]

        # Basic validation
        if tag_name != end_tag_name:
            print(f"Warning: Tag mismatch <{tag_name}>...</{end_tag_name}>")

        node = Node(tag=str(tag_name), attributes=attrs)
        for child in children:
            node.add_child(child)
        return node

    def self_closing_tag(self, items):
        tag_name = items[0]
        attrs = items[1]
        return Node(tag=str(tag_name), attributes=attrs)

    def attributes(self, items):
        return {k: v for k, v in items}

    def attribute(self, items):
        key = str(items[0])
        value = items[1] if len(items) > 1 else None
        return (key, value)

    def string_value(self, items):
        return items[0].strip('"\'')

    def python_value(self, items):
        # Extract content from the Python Node
        return items[0].value

    def python_block(self, items):
        # items[0] is "{ code }". We strip braces to get clean code.
        raw_code = items[0].value if isinstance(items[0], Token) else items[0]
        code = raw_code.strip("{} ").strip()
        # We mark it as a 'python' tag node so the renderer knows to evaluate it
        return Node(tag="python", value=code)

    def text(self, items):
        return Node(value=str(items[0]))


class Parser:
    def __init__(self):
        self.lark = Lark(grammar, start='start', parser='lalr', transformer=XpymlTransformer())

    def parse(self, text):
        # Returns the root node
        return self.lark.parse(text)