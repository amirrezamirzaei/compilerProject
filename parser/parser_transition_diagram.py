import json
from scanner import Reader, ScannerResult, get_next_token
from anytree import Node
from scanner.const import TokenType


def parse_transition_diagram():
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
        self.parsing_EOF = False  # will be set to True when unexpected EOF occurs
        self.parsing_stack = []

    def parse(self):
        root = Node("Program")
        self.parsing_stack = [(self.parse_Program, root)]
        while self.parsing_stack and not self.parsing_EOF:
            top_stack = self.parsing_stack.pop()
            if hasattr(top_stack[0], '__call__'):
                func, tree = top_stack
                func(tree)
            else:
                terminal, tree = top_stack
                self.match_terminal(terminal, tree)
        return root, self.errors

    def parse_Program(self, node):
        token = self.get_terminal()
        # Program -> Declaration-list $

        if self.is_in_first('Declaration-list', token):
            self.parsing_stack.append(('$', node))
            self.parsing_stack.append((self.parse_Declaration_list, node))
        else:  # error
            pass

    def parse_Declaration_list(self, node):
        token = self.get_terminal()
        node = Node("Declaration-list", parent=node)

        # Declaration-list -> Declaration Declaration-list
        if self.is_in_first('Declaration', token):
            self.parsing_stack.append((self.parse_Declaration_list, node))
            self.parsing_stack.append((self.parse_Declaration, node))
        # Declaration-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Declaration']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration-list', token):
                self.parsing_stack.append((self.parse_Declaration_list, parent))

    def parse_Declaration(self, node):
        token = self.get_terminal()
        node = Node("Declaration", parent=node)

        # Declaration -> Declaration-initial Declaration-prime
        if self.is_in_first('Declaration-initial', token):
            self.parsing_stack.append((self.parse_Declaration_prime, node))
            self.parsing_stack.append((self.parse_Declaration_initial, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration', token):
                self.parsing_stack.append((self.parse_Declaration, parent))

    def parse_Declaration_initial(self, node):
        token = self.get_terminal()
        node = Node("Declaration-initial", parent=node)

        # Declaration-initial ->  Type-specifier ID
        if self.is_in_first('Type-specifier', token):
            self.parsing_stack.append(('ID', node))
            self.parsing_stack.append((self.parse_Type_specifier, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration-initial', token):
                self.parsing_stack.append((self.parse_Declaration_initial, parent))

    def parse_Declaration_prime(self, node):
        token = self.get_terminal()
        node = Node("Declaration-prime", parent=node)

        # Declaration-prime -> Fun-declaration-prime
        if self.is_in_first('Fun-declaration-prime', token):
            self.parsing_stack.append((self.parse_Fun_declaration_prime, node))
        # Declaration-prime -> Var-declaration-prime
        elif self.is_in_first('Var-declaration-prime', token):
            self.parsing_stack.append((self.parse_Var_declaration_prime, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Declaration-prime', token):
                self.parsing_stack.append((self.parse_Declaration_prime, parent))

    def parse_Var_declaration_prime(self, node):
        token = self.get_terminal()
        node = Node("Var-declaration-prime", parent=node)

        # Var-declaration-prime -> ;
        if token.get_terminal_form() == ';':
            self.parsing_stack.append((';', node))
        # Var-declaration-prime -> [ NUM ] ;
        elif token.get_terminal_form() == '[':
            self.parsing_stack.append((';', node))
            self.parsing_stack.append((']', node))
            self.parsing_stack.append(('NUM', node))
            self.parsing_stack.append(('[', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Var-declaration-prime', token):
                self.parsing_stack.append((self.parse_Var_declaration_prime, parent))

    def parse_Fun_declaration_prime(self, node):
        token = self.get_terminal()
        node = Node("Fun-declaration-prime", parent=node)

        # Fun-declaration-prime ->  ( Params ) Compound-stmt
        if token.get_terminal_form() == '(':
            self.parsing_stack.append((self.parse_Compound_stmt, node))
            self.parsing_stack.append((')', node))
            self.parsing_stack.append((self.parse_Params, node))
            self.parsing_stack.append(('(', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Fun-declaration-prime', token):
                self.parsing_stack.append((self.parse_Fun_declaration_prime, parent))

    def parse_Type_specifier(self, node):
        token = self.get_terminal()
        node = Node("Type-specifier", parent=node)

        # Type - specifier -> int
        if token.get_terminal_form() == 'int':
            self.parsing_stack.append(('int', node))
        # Type - specifier -> void
        elif token.get_terminal_form() == 'void':
            self.parsing_stack.append(('void', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Type-specifier', token):
                self.parsing_stack.append((self.parse_Type_specifier, parent))

    def parse_Params(self, node):
        token = self.get_terminal()
        node = Node("Params", parent=node)

        # Params -> int ID Param-prime Param-list
        if token.get_terminal_form() == 'int':
            self.parsing_stack.append((self.parse_Param_list, node))
            self.parsing_stack.append((self.parse_Param_prime, node))
            self.parsing_stack.append(('ID', node))
            self.parsing_stack.append(('int', node))
        # Params -> void
        elif token.get_terminal_form() == 'void':
            self.parsing_stack.append(('void', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Params', token):
                self.parsing_stack.append((self.parse_Params, parent))

    def parse_Param_list(self, node):
        token = self.get_terminal()
        node = Node("Param-list", parent=node)

        # Param-list -> , Param Param-list
        if token.get_terminal_form() == ',':
            self.parsing_stack.append((self.parse_Param_list, node))
            self.parsing_stack.append((self.parse_Param, node))
            self.parsing_stack.append((',', node))
        # Param-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Param-list']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Param-list', token):
                self.parsing_stack.append((self.parse_Param_list, parent))

    def parse_Param(self, node):
        token = self.get_terminal()
        node = Node("Param", parent=node)

        # Param -> Declaration-initial Param-prime
        if self.is_in_first('Declaration-initial', token):
            self.parsing_stack.append((self.parse_Param_prime, node))
            self.parsing_stack.append((self.parse_Declaration_initial, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Param', token):
                self.parsing_stack.append((self.parse_Param, parent))

    def parse_Param_prime(self, node):
        token = self.get_terminal()
        node = Node("Param-prime", parent=node)

        # Param-prime -> [  ]
        if token.get_terminal_form() == '[':
            self.parsing_stack.append((']', node))
            self.parsing_stack.append(('[', node))
        # Param-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Param-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Param-prime', token):
                self.parsing_stack.append((self.parse_Param_prime, parent))

    def parse_Compound_stmt(self, node):
        token = self.get_terminal()
        node = Node("Compound-stmt", parent=node)

        # Compound-stmt -> { Declaration-list Statement-list }
        if token.get_terminal_form() == '{':
            self.parsing_stack.append(('}', node))
            self.parsing_stack.append((self.parse_Statement_list, node))
            self.parsing_stack.append((self.parse_Declaration_list, node))
            self.parsing_stack.append(('{', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Compound-stmt', token):
                self.parsing_stack.append((self.parse_Compound_stmt, parent))

    def parse_Statement_list(self, node):
        token = self.get_terminal()
        node = Node("Statement-list", parent=node)

        # Statement-list -> Statement Statement-list
        if self.is_in_first('Statement', token):
            self.parsing_stack.append((self.parse_Statement_list, node))
            self.parsing_stack.append((self.parse_Statement, node))
        # Statement-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Statement-list']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Statement-list', token):
                self.parsing_stack.append((self.parse_Statement_list, parent))

    def parse_Statement(self, node):
        token = self.get_terminal()
        node = Node("Statement", parent=node)

        # Statement -> Expression-stmt
        if self.is_in_first('Expression-stmt', token):
            self.parsing_stack.append((self.parse_Expression_stmt, node))
        # Statement -> Compound-stmt
        elif self.is_in_first('Compound-stmt', token):
            self.parsing_stack.append((self.parse_Compound_stmt, node))
        # Statement -> Selection-stmt
        elif self.is_in_first('Selection-stmt', token):
            self.parsing_stack.append((self.parse_Selection_stmt, node))
        # Statement -> Iteration-stmt
        elif self.is_in_first('Iteration-stmt', token):
            self.parsing_stack.append((self.parse_Iteration_stmt, node))
        # Statement -> Return-stmt
        elif self.is_in_first('Return-stmt', token):
            self.parsing_stack.append((self.parse_Return_stmt, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Statement', token):
                self.parsing_stack.append((self.parse_Statement, parent))

    def parse_Expression_stmt(self, node):
        token = self.get_terminal()
        node = Node("Expression-stmt", parent=node)

        # Expression-stmt -> Expression ;
        if self.is_in_first('Expression', token):
            self.parsing_stack.append((';', node))
            self.parsing_stack.append((self.parse_Expression, node))
        # Expression-stmt -> break ;
        elif token.get_terminal_form() == 'break':
            self.parsing_stack.append((';', node))
            self.parsing_stack.append(('break', node))
        #  Expression-stmt -> ;
        elif token.get_terminal_form() == ';':
            self.parsing_stack.append((';', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Expression-stmt', token):
                self.parsing_stack.append((self.parse_Expression_stmt, parent))

    def parse_Selection_stmt(self, node):
        token = self.get_terminal()
        node = Node("Selection-stmt", parent=node)

        # Selection-stmt -> if ( Expression ) Statement Else-stmt
        if token.get_terminal_form() == 'if':
            self.parsing_stack.append((self.parse_Else_stmt, node))
            self.parsing_stack.append((self.parse_Statement, node))
            self.parsing_stack.append((')', node))
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('(', node))
            self.parsing_stack.append(('if', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Selection-stmt', token):
                self.parsing_stack.append((self.parse_Selection_stmt, parent))

    def parse_Else_stmt(self, node):
        token = self.get_terminal()
        node = Node("Else-stmt", parent=node)

        # Else-stmt -> endif
        if token.get_terminal_form() == 'endif':
            self.parsing_stack.append(('endif', node))
        #  Else-stmt -> else Statement endif
        elif token.get_terminal_form() == 'else':
            self.parsing_stack.append(('endif', node))
            self.parsing_stack.append((self.parse_Statement, node))
            self.parsing_stack.append(('else', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Else-stmt', token):
                self.parsing_stack.append((self.parse_Else_stmt, parent))

    def parse_Iteration_stmt(self, node):
        token = self.get_terminal()
        node = Node("Iteration-stmt", parent=node)

        # Iteration-stmt -> repeat Statement until ( Expression )
        if token.get_terminal_form() == 'repeat':
            self.parsing_stack.append((')', node))
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('(', node))
            self.parsing_stack.append(('until', node))
            self.parsing_stack.append((self.parse_Statement, node))
            self.parsing_stack.append(('repeat', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Iteration-stmt', token):
                self.parsing_stack.append((self.parse_Iteration_stmt, parent))

    def parse_Return_stmt(self, node):
        token = self.get_terminal()
        node = Node("Return-stmt", parent=node)

        # Return-stmt -> return Return-stmt-prime
        if token.get_terminal_form() == 'return':
            self.parsing_stack.append((self.parse_Return_stmt_prime, node))
            self.parsing_stack.append(('return', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Return-stmt', token):
                self.parsing_stack.append((self.parse_Return_stmt, parent))

    def parse_Return_stmt_prime(self, node):
        token = self.get_terminal()
        node = Node("Return-stmt-prime", parent=node)

        # Return-stmt-prime -> ;
        if token.get_terminal_form() == ';':
            self.parsing_stack.append((';', node))
        # Return-stmt-prime -> Expression ;
        elif self.is_in_first('Expression', token):
            self.parsing_stack.append((';', node))
            self.parsing_stack.append((self.parse_Expression, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Return-stmt-prime', token):
                self.parsing_stack.append((self.parse_Return_stmt_prime, parent))

    def parse_Expression(self, node):
        token = self.get_terminal()
        node = Node("Expression", parent=node)

        # Expression -> Simple-expression-zegond | ID B
        if self.is_in_first('Simple-expression-zegond', token):
            self.parsing_stack.append((self.parse_Simple_expression_zegond, node))
        # Expression -> ID B
        elif token.get_terminal_form() == 'ID':
            self.parsing_stack.append((self.parse_B, node))
            self.parsing_stack.append(('ID', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Expression', token):
                self.parsing_stack.append((self.parse_Expression, parent))

    def parse_B(self, node):
        token = self.get_terminal()
        node = Node("B", parent=node)

        # B -> = Expression
        if token.get_terminal_form() == '=':
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('=', node))
        # B -> [ Expression ] H
        elif token.get_terminal_form() == '[':
            self.parsing_stack.append((self.parse_H, node))
            self.parsing_stack.append((']', node))
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('[', node))
        # B -> Simple-expression-prime
        elif self.is_in_first('Simple-expression-prime', token):
            self.parsing_stack.append((self.parse_Simple_expression_prime, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('B', token):
                self.parsing_stack.append((self.parse_B, parent))

    def parse_H(self, node):
        token = self.get_terminal()
        node = Node("H", parent=node)

        # H -> = Expression
        if token.get_terminal_form() == '=':
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('=', node))
        # H -> G D C
        elif self.is_in_first('G', token):
            self.parsing_stack.append((self.parse_C, node))
            self.parsing_stack.append((self.parse_D, node))
            self.parsing_stack.append((self.parse_G, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('H', token):
                self.parsing_stack.append((self.parse_H, parent))

    def parse_Simple_expression_zegond(self, node):
        token = self.get_terminal()
        node = Node("Simple-expression-zegond", parent=node)

        # Simple-expression-zegond -> Additive-expression-zegond C
        if self.is_in_first('Additive-expression-zegond', token):
            self.parsing_stack.append((self.parse_C, node))
            self.parsing_stack.append((self.parse_Additive_expression_zegond, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Simple-expression-zegond', token):
                self.parsing_stack.append((self.parse_Simple_expression_zegond, parent))

    def parse_Simple_expression_prime(self, node):
        token = self.get_terminal()
        node = Node("Simple-expression-prime", parent=node)

        # Simple-expression-prime -> Additive-expression-prime C
        if self.is_in_first('Additive-expression-prime', token):
            self.parsing_stack.append((self.parse_C, node))
            self.parsing_stack.append((self.parse_Additive_expression_prime, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Simple-expression-prime', token):
                self.parsing_stack.append((self.parse_Simple_expression_prime, parent))

    def parse_C(self, node):
        token = self.get_terminal()
        node = Node("C", parent=node)

        # C -> Relop Additive-expression
        if self.is_in_first('Relop', token):
            self.parsing_stack.append((self.parse_Additive_expression, node))
            self.parsing_stack.append((self.parse_Relop, node))
        # C -> EPSILON
        elif token.get_terminal_form() in self.grammar['C']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('C', token):
                self.parsing_stack.append((self.parse_C, parent))

    def parse_Relop(self, node):
        token = self.get_terminal()
        node = Node("Relop", parent=node)

        # Relop -> <
        if token.get_terminal_form() == '<':
            self.parsing_stack.append(('<', node))
        # Relop -> ==
        elif token.get_terminal_form() == '==':
            self.parsing_stack.append(('==', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Relop', token):
                self.parsing_stack.append((self.parse_Relop, parent))

    def parse_Additive_expression(self, node):
        token = self.get_terminal()
        node = Node("Additive-expression", parent=node)

        # Additive-expression -> Term D
        if self.is_in_first('Term', token):
            self.parsing_stack.append((self.parse_D, node))
            self.parsing_stack.append((self.parse_Term, node))
        else:  # errors
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Additive-expression', token):
                self.parsing_stack.append((self.parse_Additive_expression, parent))

    def parse_Additive_expression_prime(self, node):
        token = self.get_terminal()
        node = Node("Additive-expression-prime", parent=node)

        # Additive-expression-prime -> Term-prime D
        if self.is_in_first('Term-prime', token):
            self.parsing_stack.append((self.parse_D, node))
            self.parsing_stack.append((self.parse_Term_prime, node))
        else:  # errors
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Additive-expression-prime', token):
                self.parsing_stack.append((self.parse_Additive_expression_prime, parent))

    def parse_Additive_expression_zegond(self, node):
        token = self.get_terminal()
        node = Node("Additive-expression-zegond", parent=node)

        # Additive-expression-zegond -> Term-zegond D
        if self.is_in_first('Term-zegond', token):
            self.parsing_stack.append((self.parse_D, node))
            self.parsing_stack.append((self.parse_Term_zegond, node))
        else:  # prime
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Additive-expression-zegond', token):
                self.parsing_stack.append((self.parse_Additive_expression_zegond, parent))

    def parse_D(self, node):
        token = self.get_terminal()
        node = Node("D", parent=node)

        # D -> Addop Term D
        if self.is_in_first('Addop', token):
            self.parsing_stack.append((self.parse_D, node))
            self.parsing_stack.append((self.parse_Term, node))
            self.parsing_stack.append((self.parse_Addop, node))
        # D -> EPSILON
        elif token.get_terminal_form() in self.grammar['D']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('D', token):
                self.parsing_stack.append((self.parse_D, parent))

    def parse_Addop(self, node):
        token = self.get_terminal()
        node = Node("Addop", parent=node)

        # Addop -> +
        if token.get_terminal_form() == '+':
            self.parsing_stack.append(('+', node))
        # Addop -> -
        elif token.get_terminal_form() == '-':
            self.parsing_stack.append(('-', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Addop', token):
                self.parsing_stack.append((self.parse_Addop, parent))

    def parse_Term(self, node):
        token = self.get_terminal()
        node = Node("Term", parent=node)

        # Term -> Factor G
        if self.is_in_first('Factor', token):
            self.parsing_stack.append((self.parse_G, node))
            self.parsing_stack.append((self.parse_Factor, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Term', token):
                self.parsing_stack.append((self.parse_Term, parent))

    def parse_Term_prime(self, node):
        token = self.get_terminal()
        node = Node("Term-prime", parent=node)

        # Term-prime -> Factor-prime G
        if self.is_in_first('Factor-prime', token):
            self.parsing_stack.append((self.parse_G, node))
            self.parsing_stack.append((self.parse_Factor_prime, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Term-prime', token):
                self.parsing_stack.append((self.parse_Term_prime, parent))

    def parse_Term_zegond(self, node):
        token = self.get_terminal()
        node = Node("Term-zegond", parent=node)

        # Term-zegond -> Factor-zegond G
        if self.is_in_first('Factor-zegond', token):
            self.parsing_stack.append((self.parse_G, node))
            self.parsing_stack.append((self.parse_Factor_zegond, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Term-zegond', token):
                self.parsing_stack.append((self.parse_Term_zegond, parent))

    def parse_G(self, node):
        token = self.get_terminal()
        node = Node("G", parent=node)

        # G -> * Factor G
        if token.get_terminal_form() == '*':
            self.parsing_stack.append((self.parse_G, node))
            self.parsing_stack.append((self.parse_Factor, node))
            self.parsing_stack.append(('*', node))
        # G -> EPSILON
        elif token.get_terminal_form() in self.grammar['G']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('G', token):
                self.parsing_stack.append((self.parse_G, parent))

    def parse_Factor(self, node):
        token = self.get_terminal()
        node = Node("Factor", parent=node)

        # Factor -> ( Expression )
        if token.get_terminal_form() == '(':
            self.parsing_stack.append((')', node))
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('(', node))
        # Factor -> ID Var-call-prime
        elif token.get_terminal_form() == 'ID':
            self.parsing_stack.append((self.parse_Var_call_prime, node))
            self.parsing_stack.append(('ID', node))
        # Factor -> NUM
        elif token.get_terminal_form() == 'NUM':
            self.parsing_stack.append(('NUM', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Factor', token):
                self.parsing_stack.append((self.parse_Factor, parent))

    def parse_Var_call_prime(self, node):
        token = self.get_terminal()
        node = Node("Var-call-prime", parent=node)

        # Var-call-prime -> ( Args )
        if token.get_terminal_form() == '(':
            self.parsing_stack.append((')', node))
            self.parsing_stack.append((self.parse_Args, node))
            self.parsing_stack.append(('(', node))
        # Var-call-prime -> Var-prime
        elif self.is_in_first('Var-prime', token):
            self.parsing_stack.append((self.parse_Var_prime, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Var-call-prime', token):
                self.parsing_stack.append((self.parse_Var_call_prime, parent))

    def parse_Var_prime(self, node):
        token = self.get_terminal()
        node = Node("Var-prime", parent=node)

        # Var-prime -> [ Expression ]
        if token.get_terminal_form() == '[':
            self.parsing_stack.append((']', node))
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('[', node))
        # Var-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Var-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Var-prime', token):
                self.parsing_stack.append((self.parse_Var_prime, parent))

    def parse_Factor_prime(self, node):
        token = self.get_terminal()
        node = Node("Factor-prime", parent=node)

        # Factor-prime -> ( Args )
        if token.get_terminal_form() == '(':
            self.parsing_stack.append((')', node))
            self.parsing_stack.append((self.parse_Args, node))
            self.parsing_stack.append(('(', node))
        # Factor-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Factor-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Factor-prime', token):
                self.parsing_stack.append((self.parse_Factor_prime, parent))

    def parse_Factor_zegond(self, node):
        token = self.get_terminal()
        node = Node("Factor-zegond", parent=node)

        # Factor-zegond -> ( Expression )
        if token.get_terminal_form() == '(':
            self.parsing_stack.append((')', node))
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append(('(', node))
        # Factor-zegond -> NUM
        elif token.get_terminal_form() == 'NUM':
            self.parsing_stack.append(('NUM', node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Factor-zegond', token):
                self.parsing_stack.append((self.parse_Factor_zegond, parent))

    def parse_Args(self, node):
        token = self.get_terminal()
        node = Node("Args", parent=node)

        # Args -> Arg-list
        if self.is_in_first('Arg-list', token):
            self.parsing_stack.append((self.parse_Arg_list, node))
        # Args -> EPSILON
        elif token.get_terminal_form() in self.grammar['Args']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Args', token):
                self.parsing_stack.append((self.parse_Args, parent))

    def parse_Arg_list(self, node):
        token = self.get_terminal()
        node = Node("Arg-list", parent=node)

        # Arg-list -> Expression Arg-list-prime
        if self.is_in_first('Expression', token):
            self.parsing_stack.append((self.parse_Arg_list_prime, node))
            self.parsing_stack.append((self.parse_Expression, node))
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Arg-list', token):
                self.parsing_stack.append((self.parse_Arg_list, parent))

    def parse_Arg_list_prime(self, node):
        token = self.get_terminal()
        node = Node("Arg-list-prime", parent=node)

        # Arg-list-prime -> , Expression Arg-list-prime
        if token.get_terminal_form() == ',':
            self.parsing_stack.append((self.parse_Arg_list_prime, node))
            self.parsing_stack.append((self.parse_Expression, node))
            self.parsing_stack.append((',', node))
        # Arg-list-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Arg-list-prime']['Follow']:
            Node("epsilon", parent=node)
        else:  # error
            parent = node.parent
            node.parent = None
            if not self.handle_error_non_terminal('Arg-list-prime', token):
                self.parsing_stack.append((self.parse_Arg_list_prime, parent))

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
                self.parsing_EOF = True
                self.errors.append(f'#{self.current_token.line} : syntax error, Unexpected EOF')
                return True
            return False
