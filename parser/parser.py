import json
from scanner import Reader, ScannerResult, get_next_token
from anytree import Node
from scanner.const import TokenType


def parse():
    t = TransitionDiagram(Reader('input.txt'), ScannerResult())
    tree, errors = t.parse()
    return tree, errors


class TransitionDiagram:

    def __init__(self, reader, out):
        self.reader = reader
        self.out = out
        self.current_token = None
        self.grammar = json.load(open('parser/grammar.json'))
        self.errors = []
        self.parsing_EOF = True  # will be set to False when unexpected EOF occurs

    def parse(self):
        tree = self.parse_Program()
        return tree, self.errors

    def parse_Program(self):
        token = self.get_terminal()
        root = Node("Program")
        self.root = root

        # Program -> Declaration-list $
        if self.is_in_first('Declaration-list', token):
            self.parse_Declaration_list(root)
            if self.parsing_EOF:
                Node("$", parent=root)
        else:  # error
            root = Node("Program")
            if not self.handle_error_non_terminal('Program', token):
                self.parse_Program(root)
        return root

    def parse_Declaration_list(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Declaration-list", parent=node)

        # Declaration-list -> Declaration Declaration-list
        if self.is_in_first('Declaration', token):
            self.parse_Declaration(node)
            self.parse_Declaration_list(node)
        # Declaration-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Declaration']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration_list', token):
                self.parse_Declaration_list(parent)

    def parse_Declaration(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Declaration", parent=node)

        # Declaration -> Declaration-initial Declaration-prime
        if self.is_in_first('Declaration-initial', token):
            self.parse_Declaration_initial(node)
            self.parse_Declaration_prime(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration', token):
                self.parse_Declaration(parent)

    def parse_Declaration_initial(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Declaration-initial", parent=node)

        # Declaration-initial ->  Type-specifier ID
        if self.is_in_first('Type-specifier', token):
            self.parse_Type_specifier(node)
            self.match_terminal('ID', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration-initial', token):
                self.parse_Declaration_initial(parent)

    def parse_Declaration_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Declaration-prime", parent=node)

        # Declaration-prime -> Fun-declaration-prime
        if self.is_in_first('Fun-declaration-prime', token):
            self.parse_Fun_declaration_prime(node)
        # Declaration-prime -> Var-declaration-prime
        elif self.is_in_first('Var-declaration-prime', token):
            self.parse_Var_declaration_prime(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration-prime', token):
                self.parse_Declaration_prime(parent)

    def parse_Var_declaration_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Var-declaration-prime", parent=node)

        # Var-declaration-prime -> ;
        if token.get_terminal_form() == ';':
            self.match_terminal(';', node)
        # Var-declaration-prime -> [ NUM ] ;
        elif token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.match_terminal('NUM', node)
            self.match_terminal(']', node)
            self.match_terminal(';', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Var-declaration-prime', token):
                self.parse_Var_declaration_prime(parent)

    def parse_Fun_declaration_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Fun-declaration-prime", parent=node)

        # Fun-declaration-prime ->  ( Params ) Compound-stmt
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Params(node)
            self.match_terminal(')', node)
            self.parse_Compound_stmt(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Fun-declaration-prime', token):
                self.parse_Fun_declaration_prime(parent)

    def parse_Type_specifier(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Type-specifier", parent=node)

        # Type - specifier -> int
        if token.get_terminal_form() == 'int':
            self.match_terminal('int', node)
        # Type - specifier -> void
        elif token.get_terminal_form() == 'void':
            self.match_terminal('void', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Type-specifier', token):
                self.parse_Type_specifier(parent)

    def parse_Params(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Params", parent=node)

        # Params -> int ID Param-prime Param-list
        if token.get_terminal_form() == 'int':
            self.match_terminal('int', node)
            self.match_terminal('ID', node)
            self.parse_Param_prime(node)
            self.parse_Param_list(node)
        # Params -> void
        elif token.get_terminal_form() == 'void':
            self.match_terminal('void', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Params', token):
                self.parse_Params(parent)

    def parse_Param_list(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Param-list", parent=node)

        # Param-list -> , Param Param-list
        if token.get_terminal_form() == ',':
            self.match_terminal(',', node)
            self.parse_Param(node)
            self.parse_Param_list(node)
        # Param-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Param-list']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Param-list', token):
                self.parse_Param_list(parent)

    def parse_Param(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Param", parent=node)

        # Param -> Declaration-initial Param-prime
        if self.is_in_first('Declaration-initial', token):
            self.parse_Declaration_initial(node)
            self.parse_Param_prime(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Param', token):
                self.parse_Param(parent)

    def parse_Param_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Param-prime", parent=node)

        # Param-prime -> [  ]
        if token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.match_terminal(']', node)
        # Param-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Param-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Param-prime', token):
                self.parse_Param_prime(parent)

    def parse_Compound_stmt(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Compound-stmt", parent=node)

        # Compound-stmt -> { Declaration-list Statement-list }
        if token.get_terminal_form() == '{':
            self.match_terminal('{', node)
            self.parse_Declaration_list(node)
            self.parse_Statement_list(node)
            self.match_terminal('}', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Compound-stmt', token):
                self.parse_Compound_stmt(parent)

    def parse_Statement_list(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Statement-list", parent=node)

        # Statement-list -> Statement Statement-list
        if self.is_in_first('Statement', token):
            self.parse_Statement(node)
            self.parse_Statement_list(node)
        # Statement-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Statement-list']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Statement-list', token):
                self.parse_Statement_list(parent)

    def parse_Statement(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Statement", parent=node)

        # Statement -> Expression-stmt
        if self.is_in_first('Expression-stmt', token):
            self.parse_Expression_stmt(node)
        # Statement -> Compound-stmt
        elif self.is_in_first('Compound-stmt', token):
            self.parse_Compound_stmt(node)
        # Statement -> Selection-stmt
        elif self.is_in_first('Selection-stmt', token):
            self.parse_Selection_stmt(node)
        # Statement -> Iteration-stmt
        elif self.is_in_first('Iteration-stmt', token):
            self.parse_Iteration_stmt(node)
        # Statement -> Return-stmt
        elif self.is_in_first('Return-stmt', token):
            self.parse_Return_stmt(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Statement', token):
                self.parse_Statement(parent)

    def parse_Expression_stmt(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Expression-stmt", parent=node)

        # Expression-stmt -> Expression ;
        if self.is_in_first('Expression', token):
            self.parse_Expression(node)
            self.match_terminal(';', node)
        # Expression-stmt -> break ;
        elif token.get_terminal_form() == 'break':
            self.match_terminal('break', node)
            self.match_terminal(';', node)
        #  Expression-stmt -> ;
        elif token.get_terminal_form() == ';':
            self.match_terminal(';', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Expression-stmt', token):
                self.parse_Expression_stmt(parent)

    def parse_Selection_stmt(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Selection-stmt", parent=node)

        # Selection-stmt -> if ( Expression ) Statement Else-stmt
        if token.get_terminal_form() == 'if':
            self.match_terminal('if', node)
            self.match_terminal('(', node)
            self.parse_Expression(node)
            self.match_terminal(')', node)
            self.parse_Statement(node)
            self.parse_Else_stmt(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Selection-stmt', token):
                self.parse_Selection_stmt(parent)

    def parse_Else_stmt(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Else-stmt", parent=node)

        # Else-stmt -> endif
        if token.get_terminal_form() == 'endif':
            self.match_terminal('endif', node)
        #  Else-stmt -> else Statement endif
        elif token.get_terminal_form() == 'else':
            self.match_terminal('else', node)
            self.parse_Statement(node)
            self.match_terminal('endif', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Else-stmt', token):
                self.parse_Else_stmt(parent)

    def parse_Iteration_stmt(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Iteration-stmt", parent=node)

        # Iteration-stmt -> repeat Statement until ( Expression )
        if token.get_terminal_form() == 'repeat':
            self.match_terminal('repeat', node)
            self.parse_Statement(node)
            self.match_terminal('until', node)
            self.match_terminal('(', node)
            self.parse_Expression(node)
            self.match_terminal(')', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Iteration-stmt', token):
                self.parse_Iteration_stmt(parent)

    def parse_Return_stmt(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Return-stmt", parent=node)

        # Return-stmt -> return Return-stmt-prime
        if token.get_terminal_form() == 'return':
            self.match_terminal('return', node)
            self.parse_Return_stmt_prime(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Return-stmt', token):
                self.parse_Return_stmt(parent)

    def parse_Return_stmt_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Return-stmt-prime", parent=node)

        # Return-stmt-prime -> ;
        if token.get_terminal_form() == ';':
            self.match_terminal(';', node)
        # Return-stmt-prime -> Expression ;
        elif self.is_in_first('Expression', token):
            self.parse_Expression(node)
            self.match_terminal(';', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Return-stmt-prime', token):
                self.parse_Return_stmt_prime(parent)

    def parse_Expression(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Expression", parent=node)

        # Expression -> Simple-expression-zegond | ID B
        if self.is_in_first('Simple-expression-zegond', token):
            self.parse_Simple_expression_zegond(node)
        # Expression -> ID B
        elif token.get_terminal_form() == 'ID':
            self.match_terminal('ID', node)
            self.parse_B(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Expression', token):
                self.parse_Expression(parent)

    def parse_B(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("B", parent=node)

        # B -> = Expression
        if token.get_terminal_form() == '=':
            self.match_terminal('=', node)
            self.parse_Expression(node)
        # B -> [ Expression ] H
        elif token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.parse_Expression(node)
            self.match_terminal(']', node)
            self.parse_H(node)
        # B -> Simple-expression-prime
        elif self.is_in_first('Simple-expression-prime', token):
            self.parse_Simple_expression_prime(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('B', token):
                self.parse_B(parent)

    def parse_H(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("H", parent=node)

        # H -> = Expression
        if token.get_terminal_form() == '=':
            self.match_terminal('=', node)
            self.parse_Expression(node)
        # H -> G D C
        elif self.is_in_first('G', token):
            self.parse_G(node)
            self.parse_D(node)
            self.parse_C(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('H', token):
                self.parse_H(parent)

    def parse_Simple_expression_zegond(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Simple-expression-zegond", parent=node)

        # Simple-expression-zegond -> Additive-expression-zegond C
        if self.is_in_first('Additive-expression-zegond', token):
            self.parse_Additive_expression_zegond(node)
            self.parse_C(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Simple-expression-zegond', token):
                self.parse_Simple_expression_zegond(parent)

    def parse_Simple_expression_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Simple-expression-prime", parent=node)

        # Simple-expression-prime -> Additive-expression-prime C
        if self.is_in_first('Additive-expression-prime', token):
            self.parse_Additive_expression_prime(node)
            self.parse_C(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Simple-expression-prime', token):
                self.parse_Simple_expression_prime(parent)

    def parse_C(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("C", parent=node)

        # C -> Relop Additive-expression
        if self.is_in_first('Relop', token):
            self.parse_Relop(node)
            self.parse_Additive_expression(node)
        # C -> EPSILON
        elif token.get_terminal_form() in self.grammar['C']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('C', token):
                self.parse_C(parent)

    def parse_Relop(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Relop", parent=node)

        # Relop -> <
        if token.get_terminal_form() == '<':
            self.match_terminal('<', node)
        # Relop -> ==
        elif token.get_terminal_form() == '==':
            self.match_terminal('==', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Relop', token):
                self.parse_Relop(parent)

    def parse_Additive_expression(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Additive-expression", parent=node)

        # Additive-expression -> Term D
        if self.is_in_first('Term', token):
            self.parse_Term(node)
            self.parse_D(node)
        else:  # errors
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Additive-expression', token):
                self.parse_Additive_expression(parent)

    def parse_Additive_expression_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Additive-expression-prime", parent=node)

        # Additive-expression-prime -> Term-prime D
        if self.is_in_first('Term-prime', token):
            self.parse_Term_prime(node)
            self.parse_D(node)
        else:  # errors
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Additive-expression-prime', token):
                self.parse_Additive_expression_prime(parent)

    def parse_Additive_expression_zegond(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Additive-expression-zegond", parent=node)

        # Additive-expression-zegond -> Term-zegond D
        if self.is_in_first('Term-zegond', token):
            self.parse_Term_zegond(node)
            self.parse_D(node)
        else:  # prime
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Additive-expression-zegond', token):
                self.parse_Additive_expression_zegond(parent)

    def parse_D(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("D", parent=node)

        # D -> Addop Term D
        if self.is_in_first('Addop', token):
            self.parse_Addop(node)
            self.parse_Term(node)
            self.parse_D(node)
        # D -> EPSILON
        elif token.get_terminal_form() in self.grammar['D']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('D', token):
                self.parse_D(parent)

    def parse_Addop(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Addop", parent=node)

        # Addop -> +
        if token.get_terminal_form() == '+':
            self.match_terminal('+', node)
        # Addop -> -
        elif token.get_terminal_form() == '-':
            self.match_terminal('-', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Addop', token):
                self.parse_Addop(parent)

    def parse_Term(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Term", parent=node)

        # Term -> Factor G
        if self.is_in_first('Factor', token):
            self.parse_Factor(node)
            self.parse_G(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Term', token):
                self.parse_Term(parent)

    def parse_Term_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Term-prime", parent=node)

        # Term-prime -> Factor-prime G
        if self.is_in_first('Factor-prime', token):
            self.parse_Factor_prime(node)
            self.parse_G(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Term-prime', token):
                self.parse_Term_prime(parent)

    def parse_Term_zegond(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Term-zegond", parent=node)

        # Term-zegond -> Factor-zegond G
        if self.is_in_first('Factor-zegond', token):
            self.parse_Factor_zegond(node)
            self.parse_G(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Term-zegond', token):
                self.parse_Term_zegond(parent)

    def parse_G(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("G", parent=node)

        # G -> * Factor G
        if token.get_terminal_form() == '*':
            self.match_terminal('*', node)
            self.parse_Factor(node)
            self.parse_G(node)
        # G -> EPSILON
        elif token.get_terminal_form() in self.grammar['G']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('G', token):
                self.parse_G(parent)

    def parse_Factor(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Factor", parent=node)

        # Factor -> ( Expression )
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Expression(node)
            self.match_terminal(')', node)
        # Factor -> ID Var-call-prime
        elif token.get_terminal_form() == 'ID':
            self.match_terminal('ID', node)
            self.parse_Var_call_prime(node)
        # Factor -> NUM
        elif token.get_terminal_form() == 'NUM':
            self.match_terminal('NUM', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Factor', token):
                self.parse_Factor(parent)

    def parse_Var_call_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Var-call-prime", parent=node)

        # Var-call-prime -> ( Args )
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Args(node)
            self.match_terminal(')', node)
        # Var-call-prime -> Var-prime
        elif self.is_in_first('Var-prime', token):
            self.parse_Var_prime(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Var-call-prime', token):
                self.parse_Var_call_prime(parent)

    def parse_Var_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Var-prime", parent=node)

        # Var-prime -> [ Expression ]
        if token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.parse_Expression(node)
            self.match_terminal(']', node)
        # Var-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Var-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Var-prime', token):
                self.parse_Var_prime(parent)

    def parse_Factor_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Factor-prime", parent=node)

        # Factor-prime -> ( Args )
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Args(node)
            self.match_terminal(')', node)
        # Factor-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Factor-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Factor-prime', token):
                self.parse_Factor_prime(parent)

    def parse_Factor_zegond(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Factor-zegond", parent=node)

        # Factor-zegond -> ( Expression )
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Expression(node)
            self.match_terminal(')', node)
        # Factor-zegond -> NUM
        elif token.get_terminal_form() == 'NUM':
            self.match_terminal('NUM', node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Factor-zegond', token):
                self.parse_Factor_zegond(parent)

    def parse_Args(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Args", parent=node)

        # Args -> Arg-list
        if self.is_in_first('Arg-list', token):
            self.parse_Arg_list(node)
        # Args -> EPSILON
        elif token.get_terminal_form() in self.grammar['Args']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Args', token):
                self.parse_Args(parent)

    def parse_Arg_list(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Arg-list", parent=node)

        # Arg-list -> Expression Arg-list-prime
        if self.is_in_first('Expression', token):
            self.parse_Expression(node)
            self.parse_Arg_list_prime(node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Arg-list', token):
                self.parse_Arg_list(parent)

    def parse_Arg_list_prime(self, node):
        if not self.parsing_EOF:
            return
        token = self.get_terminal()
        node = Node("Arg-list-prime", parent=node)

        # Arg-list-prime -> , Expression Arg-list-prime | EPSILON
        if token.get_terminal_form() == ',':
            self.match_terminal(',', node)
            self.parse_Expression(node)
            self.parse_Arg_list_prime(node)
        # Arg-list-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Arg-list-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Arg-list-prime', token):
                self.parse_Arg_list_prime(parent)

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
            if self.parsing_EOF:
                self.errors.append(f'#{self.current_token.line} : syntax error, missing {terminal}')

    def is_in_first(self, non_terminal, token):
        return token.get_terminal_form() in self.grammar[non_terminal]['First'] or (
                'EPSILON' in self.grammar[non_terminal]['First'])

    def is_in_follow(self, non_terminal, token):
        return token.get_terminal_form() in self.grammar[non_terminal]['Follow']

    def handle_error_non_terminal(self, non_terminal, token):
        """
        will add the correct error to the error list.
        if the output is true parsing should resume.
        if output is false the current non terminal procedure must be called again.
        """

        if self.current_token.content == '$' and self.current_token.type == TokenType.END:
            return True

        if self.is_in_follow(non_terminal, token):
            self.errors.append(f'#{token.line} : syntax error, missing {non_terminal}')
            return True
        else:
            self.get_next_parse_token()
            self.errors.append(f'#{token.line} : syntax error, illegal {token.get_terminal_form()}')

            if self.current_token.content == '$' and self.current_token.type == TokenType.END:
                self.parsing_EOF = False
                self.errors.append(f'#{self.current_token.line} : syntax error, Unexpected EOF')
                return True
            return False
