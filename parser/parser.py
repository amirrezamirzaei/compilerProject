from scanner import Reader, ScannerResult, get_next_token
from anytree import Node, RenderTree
from scanner.const import TokenType


def parse():
    r = Reader('input.txt')
    out = ScannerResult()
    while True:
        print(get_next_token(r, out))
        break


class TransitionDiagram:

    def __init__(self, reader, out):
        self.reader = reader
        self.out = out
        self.current_token = None

    def get_next_parse_token(self):
        return get_next_token(self.reader, self.out)

    def parse_Program(self):
        pass

    def parse_Declaration_list(self):
        pass

    def parse_Declaration(self):
        pass

    def parse_Declaration_initial(self):
        pass

    def parse_Declaration_prime(self):
        pass

    def parse_Var_declaration_prime(self):
        pass

    def parse_Fun_declaration_prime(self):
        pass

    def parse_Type_specifier(self):
        pass

    def parse_Params(self):
        pass

    def parse_Param_list(self):
        pass

    def parse_Param(self):
        pass

    def parse_Param_prime(self):
        pass

    def parse_Compound_stmt(self):
        pass

    def parse_Statement_list(self):
        pass

    def parse_Statement(self):
        pass

    def parse_Expression_stmt(self):
        pass

    def parse_Selection_stmt(self):
        pass

    def parse_Else_stmt(self):
        pass

    def parse_Iteration_stmt(self):
        pass

    def parse_Return_stmt(self):
        pass

    def parse_Return_stmt_prime(self):
        pass

    def parse_Expression(self):
        pass

    def parse_B(self):
        pass

    def parse_H(self):
        pass

    def parse_Simple_expression_zegond(self):
        pass

    def parse_Simple_expression_prime(self):
        pass

    def parse_C(self):
        pass

    def parse_Relop(self):
        pass

    def parse_Additive_expression(self):
        pass

    def parse_Additive_expression_prime(self):
        pass

    def parse_Additive_expression_zegond(self):
        pass

    def parse_D(self):
        pass

    def parse_Addop(self):
        pass

    def parse_Term(self):
        pass

    def parse_Term_prime(self):
        pass

    def parse_Term_zegond(self):
        pass

    def parse_G(self):
        pass

    def parse_Factor(self):
        pass

    def parse_Var_call_prime(self):
        pass

    def parse_Var_prime(self):
        pass

    def parse_Factor_prime(self):
        pass

    def parse_Factor_zegond(self):
        pass

    def parse_Args(self):
        pass

    def parse_Arg_list(self):
        pass

    def parse_Arg_list_prime(self):
        pass
