import json

from scanner import Reader, ScannerResult, get_next_token
from anytree import Node



def parse():
    t = TransitionDiagram(Reader('input.txt'), ScannerResult())
    tree = t.parse()
    return tree, 'There is no syntax error.'

class TransitionDiagram:

    def __init__(self, reader, out):
        self.reader = reader
        self.out = out
        self.current_token = None
        self.grammar = json.load(open('parser/grammar.json'))

    def parse(self):
        tree = self.parse_Program()
        return tree

    def parse_Program(self):
        root = Node("Program")
        token = self.get_terminal()

        # Program -> Declaration-list $
        if self.is_in_first('Declaration-list', token):
            self.parse_Declaration_list(root)
            Node("$", parent=root)  # todo fix
        else:
            pass
        return root

    def parse_Declaration_list(self, node):
        node = Node("Declaration-list", parent=node)
        token = self.get_terminal()

        # Declaration-list -> Declaration Declaration-list
        if self.is_in_first('Declaration', token):
            self.parse_Declaration(node)
            self.parse_Declaration_list(node)
        # Declaration-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Declaration']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Declaration(self, node):
        node = Node("Declaration", parent=node)
        token = self.get_terminal()

        # Declaration -> Declaration-initial Declaration-prime
        if self.is_in_first('Declaration-initial', token):
            self.parse_Declaration_initial(node)
            self.parse_Declaration_prime(node)
        else:
            pass

    def parse_Declaration_initial(self, node):
        node = Node("Declaration-initial", parent=node)
        token = self.get_terminal()

        # Declaration-initial ->  Type-specifier ID
        if self.is_in_first('Type-specifier', token):
            self.parse_Type_specifier(node)
            self.match_terminal('ID', node)
        else:
            pass

    def parse_Declaration_prime(self, node):
        node = Node("Declaration-prime", parent=node)
        token = self.get_terminal()

        # Declaration-prime -> Fun-declaration-prime
        if self.is_in_first('Fun-declaration-prime', token):
            self.parse_Fun_declaration_prime(node)
        # Declaration-prime -> Var-declaration-prime
        elif self.is_in_first('Var-declaration-prime', token):
            self.parse_Var_declaration_prime(node)
        else:
            pass

    def parse_Var_declaration_prime(self, node):
        node = Node("Var-declaration-prime", parent=node)
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
        node = Node("Fun-declaration-prime", parent=node)
        token = self.get_terminal()

        # Fun-declaration-prime ->  ( Params ) Compound-stmt
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Params(node)
            self.match_terminal(')', node)
            self.parse_Compound_stmt(node)
        else:
            pass

    def parse_Type_specifier(self, node):
        node = Node("Type-specifier", parent=node)
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
        node = Node("Params", parent=node)
        token = self.get_terminal()

        # Params -> int ID Param-prime Param-list
        if token.get_terminal_form() == 'int':
            self.match_terminal('int', node)
            self.match_terminal('ID', node)
            self.parse_Param_prime(node)
            self.parse_Param_list(node)
        # Params -> void
        elif token.get_terminal_form() == 'void':
            self.match_terminal('void', node)
        else:
            pass

    def parse_Param_list(self, node):
        node = Node("Param-list", parent=node)
        token = self.get_terminal()

        # Param-list -> , Param Param-list
        if token.get_terminal_form() == ',':
            self.match_terminal(',', node)
            self.parse_Param(node)
            self.parse_Param_list(node)
        # Param-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Param-list']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Param(self, node):
        node = Node("Param", parent=node)
        token = self.get_terminal()

        # Param -> Declaration-initial Param-prime
        if self.is_in_first('Declaration-initial', token):
            self.parse_Declaration_initiale(node)
        else:
            pass

    def parse_Param_prime(self, node):
        node = Node("Param-prime", parent=node)
        token = self.get_terminal()

        # Param-prime -> [  ]
        if token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.match_terminal(']', node)
        # Param-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Param-prime']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Compound_stmt(self, node):
        node = Node("Compound-stmt", parent=node)
        token = self.get_terminal()

        # Compound-stmt -> { Declaration-list Statement-list }
        if token.get_terminal_form() == '{':
            self.match_terminal('{', node)
            self.parse_Declaration_list(node)
            self.parse_Statement_list(node)
            self.match_terminal('}', node)
        else:
            pass

    def parse_Statement_list(self, node):
        node = Node("Statement-list", parent=node)
        token = self.get_terminal()

        # Statement-list -> Statement Statement-list
        if self.is_in_first('Statement', token):
            self.parse_Statement(node)
            self.parse_Statement_list(node)
        # Statement-list -> EPSILON
        elif token.get_terminal_form() in self.grammar['Statement-list']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Statement(self, node):
        node = Node("Statement", parent=node)
        token = self.get_terminal()

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
        else:
            pass

    def parse_Expression_stmt(self, node):
        node = Node("Expression-stmt", parent=node)
        token = self.get_terminal()

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
        else:
            pass

    def parse_Selection_stmt(self, node):
        node = Node("Selection-stmt", parent=node)
        token = self.get_terminal()

        # Selection-stmt -> if ( Expression ) Statement Else-stmt
        if token.get_terminal_form() == 'if':
            self.match_terminal('if', node)
            self.match_terminal('(', node)
            self.parse_Expression(node)
            self.match_terminal(')', node)
            self.parse_Statement(node)
            self.parse_Else_stmt(node)
        else:
            pass

    def parse_Else_stmt(self, node):
        node = Node("Else-stmt", parent=node)
        token = self.get_terminal()

        # Else-stmt -> endif
        if token.get_terminal_form() == 'endif':
            self.match_terminal('endif', node)
        #  Else-stmt -> else Statement endif
        elif token.get_terminal_form() == 'else':
            self.match_terminal('else', node)
            self.parse_Statement(node)
            self.match_terminal('endif', node)
        else:
            pass

    def parse_Iteration_stmt(self, node):
        node = Node("Iteration-stmt", parent=node)
        token = self.get_terminal()

        # Iteration-stmt -> repeat Statement until ( Expression )
        if token.get_terminal_form() == 'repeat':
            self.match_terminal('repeat', node)
            self.parse_Statement(node)
            self.match_terminal('until', node)
            self.match_terminal('(', node)
            self.parse_Expression(node)
            self.match_terminal(')', node)
        else:
            pass

    def parse_Return_stmt(self, node):
        node = Node("Return-stmt", parent=node)
        token = self.get_terminal()

        # Return-stmt -> return Return-stmt-prime
        if token.get_terminal_form() == 'return':
            self.match_terminal('return', node)
            self.parse_Return_stmt_prime(node)
        else:
            pass

    def parse_Return_stmt_prime(self, node):
        node = Node("Return-stmt-prime", parent=node)
        token = self.get_terminal()

        # Return-stmt-prime -> ;
        if token.get_terminal_form() == ';':
            self.match_terminal(';', node)
        # Return-stmt-prime -> Expression ;
        elif self.is_in_first('Expression', token):
            self.parse_Expression(node)
            self.match_terminal(';', node)
        else:
            pass

    def parse_Expression(self, node):
        node = Node("Expression", parent=node)
        token = self.get_terminal()

        # Expression -> Simple-expression-zegond | ID B
        if self.is_in_first('Simple-expression-zegond', token):
            self.parse_Simple_expression_zegond(node)
        # Expression -> ID B
        elif token.get_terminal_form() == 'ID':
            self.match_terminal('ID', node)
            self.parse_B(node)
        else:
            pass

    def parse_B(self, node):
        node = Node("B", parent=node)
        token = self.get_terminal()

        # B -> = Expression
        if token.get_terminal_form() == '=':
            self.match_terminal('=', node)
            self.parse_Expression(node)
        # B -> [ Expression ] H
        elif token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.parse_Expression(node)
            self.match_terminal(']')
            self.parse_H(node)
        # B -> Simple-expression-prime
        elif self.is_in_first('Simple-expression-prime', token):
            self.parse_Simple_expression_prime(node)
        else:
            pass

    def parse_H(self, node):
        node = Node("H", parent=node)
        token = self.get_terminal()

        # H -> = Expression
        if token.get_terminal_form() == '=':
            self.match_terminal('=', node)
            self.parse_Expression(node)
        # H -> G D C
        elif self.is_in_first('G', token):
            self.parse_G(node)
            self.parse_D(node)
            self.parse_C(node)
        else:
            pass

    def parse_Simple_expression_zegond(self, node):
        node = Node("Simple-expression-zegond", parent=node)
        token = self.get_terminal()

        # Simple-expression-zegond -> Additive-expression-zegond C
        if self.is_in_first('Additive-expression-zegond', token):
            self.parse_Additive_expression_zegond(node)
            self.parse_C(node)
        else:
            pass

    def parse_Simple_expression_prime(self, node):
        node = Node("Simple-expression-prime", parent=node)
        token = self.get_terminal()

        # Simple-expression-prime -> Additive-expression-prime C
        if self.is_in_first('Additive-expression-prime', token):
            self.parse_Additive_expression_prime(node)
            self.parse_C(node)
        else:
            pass

    def parse_C(self, node):
        node = Node("C", parent=node)
        token = self.get_terminal()

        # C -> Relop Additive-expression
        if self.is_in_first('Relop', token):
            self.parse_Relop(node)
            self.parse_Additive_expression(node)
        # C -> EPSILON
        elif token.get_terminal_form() in self.grammar['C']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Relop(self, node):
        node = Node("Relop", parent=node)
        token = self.get_terminal()

        # Relop -> <
        if token.get_terminal_form() == '<':
            self.match_terminal('<', node)
        # Relop -> ==
        elif token.get_terminal_form() == '==':
            self.match_terminal('==', node)
        else:
            pass

    def parse_Additive_expression(self, node):
        node = Node("Additive-expression", parent=node)
        token = self.get_terminal()

        # Additive-expression -> Term D
        if self.is_in_first('Term', token):
            self.parse_Term(node)
            self.parse_D(node)
        else:
            pass

    def parse_Additive_expression_prime(self, node):
        node = Node("Additive-expression-prime", parent=node)
        token = self.get_terminal()

        # Additive-expression-prime -> Term-prime D

        if self.is_in_first('Term-prime', token):
            self.parse_Term_prime(node)
            self.parse_D(node)
        else:
            pass

    def parse_Additive_expression_zegond(self, node):
        node = Node("Additive-expression-zegond", parent=node)
        token = self.get_terminal()

        # Additive-expression-zegond -> Term-zegond D
        if self.is_in_first('Term-zegond', token):
            self.parse_Term_zegond(node)
            self.parse_D(node)
        else:
            pass

    def parse_D(self, node):
        node = Node("D", parent=node)
        token = self.get_terminal()

        # D -> Addop Term D
        if self.is_in_first('Addop', token):
            self.parse_Addop(node)
            self.parse_Term(node)
            self.parse_D(node)
        # D -> EPSILON
        elif token.get_terminal_form() in self.grammar['D']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Addop(self, node):
        node = Node("Addop", parent=node)
        token = self.get_terminal()

        # Addop -> +
        if token.get_terminal_form() == '+':
            self.match_terminal('+', node)
        # Addop -> -
        elif token.get_terminal_form() == '-':
            self.match_terminal('-', node)
        else:
            pass

    def parse_Term(self, node):
        node = Node("Term", parent=node)
        token = self.get_terminal()

        # Term -> Factor G
        if self.is_in_first('Factor', token):
            self.parse_Factor(node)
            self.parse_G(node)
        else:
            pass

    def parse_Term_prime(self, node):
        node = Node("Term-prime", parent=node)
        token = self.get_terminal()

        # Term-prime -> Factor-prime G
        if self.is_in_first('Factor-prime', token):
            self.parse_Factor_prime(node)
            self.parse_G(node)
        else:
            pass

    def parse_Term_zegond(self, node):
        node = Node("Term-zegond", parent=node)
        token = self.get_terminal()

        # Term-zegond -> Factor-zegond G
        if self.is_in_first('Factor-zegond', token):
            self.parse_Factor_zegond(node)
            self.parse_G(node)
        else:
            pass

    def parse_G(self, node):
        node = Node("G", parent=node)
        token = self.get_terminal()

        # G -> * Factor G
        if token.get_terminal_form() == '*':
            self.match_terminal('*', node)
            self.parse_Factor(node)
            self.parse_G(node)
        # G -> EPSILON
        elif token.get_terminal_form() in self.grammar['G']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Factor(self, node):
        node = Node("Factor", parent=node)
        token = self.get_terminal()

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
        else:
            pass

    def parse_Var_call_prime(self, node):
        node = Node("Var-call-prime", parent=node)
        token = self.get_terminal()

        # Var-call-prime -> ( Args )
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Args(node)
            self.match_terminal(')', node)
        # Var-call-prime -> Var-prime
        elif self.is_in_first('Var-prime', token):
            self.parse_Var_prime(node)
        else:
            pass

    def parse_Var_prime(self, node):
        node = Node("Var-prime", parent=node)
        token = self.get_terminal()

        # Var-prime -> [ Expression ]
        if token.get_terminal_form() == '[':
            self.match_terminal('[', node)
            self.parse_Expression(node)
            self.match_terminal(']', node)
        # Var-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Var-prime']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Factor_prime(self, node):
        node = Node("Factor-prime", parent=node)
        token = self.get_terminal()

        # Factor-prime -> ( Args )
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Args(node)
            self.match_terminal(')', node)
        # Factor-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Factor-prime']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Factor_zegond(self, node):
        node = Node("Factor-zegond", parent=node)
        token = self.get_terminal()

        # Factor-zegond -> ( Expression )
        if token.get_terminal_form() == '(':
            self.match_terminal('(', node)
            self.parse_Expression(node)
            self.match_terminal(')', node)
        # Factor-zegond -> NUM
        elif token.get_terminal_form() == 'NUM':
            self.match_terminal('NUM', node)
        else:
            pass

    def parse_Args(self, node):
        node = Node("Args", parent=node)
        token = self.get_terminal()

        # Args -> Arg-list
        if self.is_in_first('Arg-list', token):
            self.parse_Arg_list(node)
        # Args -> EPSILON
        elif token.get_terminal_form() in self.grammar['Args']['Follow']:
            Node("epsilon", parent=node)
        else:
            pass

    def parse_Arg_list(self, node):
        node = Node("Arg-list", parent=node)
        token = self.get_terminal()

        # Arg-list -> Expression Arg-list-prime
        if self.is_in_first('Expression', token):
            self.parse_Expression(node)
            self.parse_Arg_list_prime(node)
        else:
            pass

    def parse_Arg_list_prime(self, node):
        node = Node("Arg-list-prime", parent=node)
        token = self.get_terminal()

        # Arg-list-prime -> , Expression Arg-list-prime | EPSILON
        if token.get_terminal_form() == ',':
            self.match_terminal(',', node)
            self.parse_Arg_list_prime(node)
        # Arg-list-prime -> EPSILON
        elif token.get_terminal_form() in self.grammar['Arg-list-prime']['Follow']:
            Node("epsilon", parent=node)
        else:
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
        else:
            print(self.current_token)
            print(f'WTTTTTTTF {self.current_token.get_terminal_form()} {terminal}')
        self.current_token = None

    
    def is_in_first(self, non_terminal, token):
        return token.get_terminal_form() in self.grammar[non_terminal]['First'] or ('EPSILON' in self.grammar[non_terminal]['First'])
