import json

from scanner import Reader, ScannerResult, get_next_token
from anytree import Node, RenderTree
from scanner.const import TokenType


def parse():
    t = TransitionDiagram(Reader('input.txt'), ScannerResult())
    t.parse()


class TransitionDiagram:

    def __init__(self, reader, out):
        self.reader = reader
        self.out = out
        self.current_token = None
        self.grammar = json.load(open('parser/grammar.json'))

    def parse(self):
        root = Node("Program")
        self.parse_Program(root)
        for pre, fill, node in RenderTree(root):
            print("%s%s" % (pre, node.name))

    def parse_Program(self, node):
        token = self.get_terminal()

        # Program -> Declaration-list $
        if token.get_terminal_form() in self.grammar['Declaration-list']['First']:
            self.parse_Declaration_list(Node("Declaration_list", parent=node))
        else:
            pass
        return node

    def parse_Declaration_list(self, node):
        token = self.get_terminal()

        # Declaration-list -> Declaration Declaration-list
        if token.get_terminal_form() in self.grammar['Declaration']['First']:
            self.parse_Declaration(Node("Declaration", parent=node))
            self.parse_Declaration_list(Node("Declaration-list", parent=node))
        # Declaration-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Declaration']['Follow']:
            return
        else:
            pass

    def parse_Declaration(self, node):
        token = self.get_terminal()

        # Declaration -> Declaration-initial Declaration-prime
        if token.get_terminal_form() in self.grammar['Declaration-initial']['First']:
            self.parse_Declaration_initial(Node("Declaration_initial", parent=node))
            self.parse_Declaration_prime(Node("Declaration_prime", parent=node))
        else:
            pass

    def parse_Declaration_initial(self, node):
        token = self.get_terminal()

        # Declaration-initial ->  Type-specifier ID
        if token.get_terminal_form() in self.grammar['Type-specifier']['First']:
            self.parse_Type_specifier(Node("Type-specifier", parent=node))
            self.match_terminal('ID', node)
        else:
            pass

    def parse_Declaration_prime(self, node):
        token = self.get_terminal()

        # Declaration-prime -> Fun-declaration-prime
        if token.get_terminal_form() in self.grammar['Fun-declaration-prime']['First']:
            self.parse_Fun_declaration_prime(Node("Fun-declaration-prime", parent=node))
        # Declaration-prime -> Var-declaration-prime
        elif token.get_terminal_form() in self.grammar[' Var-declaration-prime']['First']:
            self.parse_Var_declaration_prime(Node("Var-declaration-prime", parent=node))
        else:
            pass

    def parse_Var_declaration_prime(self, node):
        token = self.get_terminal()

        # Var-declaration-prime -> ;
        if token.get_terminal_form() == ';':
            self.match_terminal(';', node)
        # Var-declaration-prime -> [ NUM ] ;
        elif token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.match_terminal('NUM', node)
            self.match_terminal(']', node)
            self.match_terminal(';', node)
        else:
            pass

    def parse_Fun_declaration_prime(self, node):
        token = self.get_terminal()

        # Fun-declaration-prime ->  ( Params ) Compound-stmt
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Params(Node("Params", parent=node))
            self.match_terminal(')', node)
            self.parse_Compound_stmt(Node("Compound-stmt", parent=node))
        else:
            pass

    def parse_Type_specifier(self, node):
        token = self.get_terminal()

        # Type - specifier -> int
        if token.get_terminal_form() == 'int':
            self.match_terminal('int', node)
        # Type - specifier -> void
        elif token.get_terminal_form() == 'void':
            self.match_terminal('void', node)
        else:
            pass

    def parse_Params(self, node):
        pass

    def parse_Param_list(self, node):
        pass

    def parse_Param(self, node):
        pass

    def parse_Param_prime(self, node):
        pass

    def parse_Compound_stmt(self, node):
        pass

    def parse_Statement_list(self, node):
        pass

    def parse_Statement(self, node):
        pass

    def parse_Expression_stmt(self, node):
        pass

    def parse_Selection_stmt(self, node):
        pass

    def parse_Else_stmt(self, node):
        pass

    def parse_Iteration_stmt(self, node):
        pass

    def parse_Return_stmt(self, node):
        pass

    def parse_Return_stmt_prime(self, node):
        pass

    def parse_Expression(self, node):
        pass

    def parse_B(self, node):
        pass

    def parse_H(self, node):
        pass

    def parse_Simple_expression_zegond(self, node):
        pass

    def parse_Simple_expression_prime(self, node):
        pass

    def parse_C(self, node):
        pass

    def parse_Relop(self, node):
        pass

    def parse_Additive_expression(self, node):
        pass

    def parse_Additive_expression_prime(self, node):
        pass

    def parse_Additive_expression_zegond(self, node):
        pass

    def parse_D(self, node):
        pass

    def parse_Addop(self, node):
        pass

    def parse_Term(self, node):
        pass

    def parse_Term_prime(self, node):
        pass

    def parse_Term_zegond(self, node):
        pass

    def parse_G(self, node):
        pass

    def parse_Factor(self, node):
        pass

    def parse_Var_call_prime(self, node):
        pass

    def parse_Var_prime(self, node):
        pass

    def parse_Factor_prime(self, node):
        pass

    def parse_Factor_zegond(self, node):
        pass

    def parse_Args(self, node):
        pass

    def parse_Arg_list(self, node):
        pass

    def parse_Arg_list_prime(self, node):
        pass

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
