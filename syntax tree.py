import cv2
import numpy as np


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def get_next_token(self):
        if self.pos >= len(self.text):
            return Token('EOF', None)

        current_char = self.text[self.pos]

        if current_char.isdigit():
            start_pos = self.pos
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
            return Token('NUMBER', int(self.text[start_pos:self.pos]))

        if current_char in '+-*/()':
            self.pos += 1
            return Token('OP', current_char)

        raise Exception(f"Invalid character: {current_char}")


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception("Invalid syntax")

    def factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return {'type': 'NUMBER', 'value': token.value}
        elif token.type == 'OP' and token.value == '(':
            self.eat('OP')
            node = self.expr()
            self.eat('OP')  # Expected ')'
            return node

    def term(self):
        node = self.factor()
        while self.current_token.value in ('*', '/'):
            op = self.current_token
            self.eat('OP')
            node = {'type': 'BINOP', 'op': op.value, 'left': node, 'right': self.factor()}
        return node

    def expr(self):
        node = self.term()
        while self.current_token.value in ('+', '-'):
            op = self.current_token
            self.eat('OP')
            node = {'type': 'BINOP', 'op': op.value, 'left': node, 'right': self.term()}
        return node

    def parse(self):
        return self.expr()


def print_syntax_tree(node, indent=0):
    if node['type'] == 'NUMBER':
        print(' ' * indent + f"NUMBER: {node['value']}")
    elif node['type'] == 'BINOP':
        print(' ' * indent + f"OPERATOR: {node['op']}")
        print_syntax_tree(node['left'], indent + 4)
        print_syntax_tree(node['right'], indent + 4)


def build_syntax_tree(expression):
    lexer = Lexer(expression)
    parser = Parser(lexer)
    return parser.parse()


def draw_syntax_tree(node, img, x, y, level=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    line_thickness = 1
    text_color = (0, 255, 0)
    box_color = (255, 255, 255)

    if 'left' in node:
        left_child_x = x - 50 * level
        left_child_y = y + 50
        cv2.line(img, (x, y), (left_child_x, left_child_y), text_color, line_thickness)
        draw_syntax_tree(node['left'], img, left_child_x, left_child_y, level + 1)

    if 'right' in node:
        right_child_x = x + 50 * level
        right_child_y = y + 50
        cv2.line(img, (x, y), (right_child_x, right_child_y), text_color, line_thickness)
        draw_syntax_tree(node['right'], img, right_child_x, right_child_y, level + 1)

    node_text = f"{node['value']}" if node['type'] == 'NUMBER' else f"{node['op']}"

    (text_width, text_height), _ = cv2.getTextSize(node_text, font, font_scale, font_thickness)

    padding = 5
    text_width += padding * 2
    text_height += padding * 2

    cv2.rectangle(img, (x - text_width // 2, y - text_height // 2), (x + text_width // 2, y + text_height // 2),
                  box_color, -1)

    cv2.putText(img, node_text, (x - text_width // 2 + padding, y + text_height // 2 - padding), font, font_scale,
                text_color, font_thickness)


expression = "1+2*3+4"
syntax_tree = build_syntax_tree(expression)

image_size = (800, 600, 3)
image = np.ones(image_size, dtype=np.uint8) * 255

root_x = image_size[0] // 3
root_y = 50
draw_syntax_tree(syntax_tree, image, root_x, root_y)

cv2.imshow("Syntax Tree", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
