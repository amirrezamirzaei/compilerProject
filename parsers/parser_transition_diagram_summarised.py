import json

from scanner import Reader, ScannerResult, get_next_token
from anytree import Node
from scanner.const import TokenType


def parse_transition_diagram_summarised():
    t = TransitionDiagramSummary(Reader('input.txt'), ScannerResult())
    tree, errors = t.parse()
    return tree, errors


class TransitionDiagramSummary:

    def __init__(self, reader, out):
        self.reader = reader
        self.out = out
        self.current_token = None
        self.grammar = json.load(open('parsers/grammar.json'))
        self.errors = []
        self.parsing_EOF = False  # will be set to True when unexpected EOF occurs
        self.parsing_stack = []

    def parse(self):
        root = Node("Program")
        self.parsing_stack = [("Program", root)]
        while self.parsing_stack and not self.parsing_EOF:
            top_stack = self.parsing_stack.pop()
            if top_stack[0] in self.grammar['TERMINALS'] or top_stack[0] == '$':
                terminal, tree = top_stack
                self.match_terminal(terminal, tree)
            else:
                non_terminal, tree = top_stack
                node = Node(non_terminal, parent=tree)
                rules = self.grammar[non_terminal]['Rules']
                token = self.get_terminal()
                flag_error = True
                for _, rule in rules.items():
                    if rule[0] == 'EPSILON' and token.get_terminal_form() in self.grammar[non_terminal]['Follow']:
                        flag_error = False
                        Node("epsilon", parent=node)
                        break
                    elif rule[0] != 'EPSILON' and \
                            ((rule[0] in self.grammar['TERMINALS']
                              and token.get_terminal_form() == rule[0]) or
                             (rule[0] not in self.grammar['TERMINALS'] and self.is_in_first(rule[0], token))):
                        flag_error = False
                        for r in range(len(rule) - 1, -1, -1):
                            self.parsing_stack.append((rule[r], node))
                        break
                if flag_error:
                    self.handle_error_non_terminal(non_terminal, token, node)
        return root.children[0], self.errors

    def get_next_parse_token(self):
        self.current_token = get_next_token(self.reader, self.out)
        return self.current_token

    def get_terminal(self):
        if self.current_token:
            return self.current_token
        else:
            self.get_next_parse_token()
            return self.current_token

    def match_terminal(self, terminal, node):
        self.get_terminal()
        if self.current_token.get_terminal_form() == terminal:
            Node(self.current_token, parent=node)
            self.current_token = None
        else:
            if not self.parsing_EOF:
                self.errors.append(f'#{self.current_token.line} : syntax error, missing {terminal}')

    def is_in_first(self, non_terminal, token):
        return token.get_terminal_form() in self.grammar[non_terminal]['First'] or \
               ('EPSILON' in self.grammar[non_terminal]['First'] and token.get_terminal_form() in
                self.grammar[non_terminal]['Follow'])

    def is_in_follow(self, non_terminal, token):
        return token.get_terminal_form() in self.grammar[non_terminal]['Follow']

    def handle_error_non_terminal(self, non_terminal, token, tree):
        """
        will add the correct error to the error list.
        if the output is true parsing should resume.
        if output is false the current non terminal procedure must be called again.
        """
        parent = tree.parent
        tree.parent = None
        if self.current_token.content == '$' and self.current_token.type == TokenType.END:
            return True

        if self.is_in_follow(non_terminal, token):
            self.errors.append(f'#{token.line} : syntax error, missing {non_terminal}')
            return True
        else:
            self.get_next_parse_token()
            self.errors.append(f'#{token.line} : syntax error, illegal {token.get_terminal_form()}')

            if self.current_token.content == '$' and self.current_token.type == TokenType.END:
                self.parsing_EOF = True
                self.errors.append(f'#{self.current_token.line} : syntax error, Unexpected EOF')
                return True

            self.parsing_stack.append((non_terminal, parent))
            return False
