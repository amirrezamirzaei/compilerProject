import sys
from enum import Enum

KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'main']


class Reader:

    def __init__(self, file_name: str):
        self.f = open(file_name, "r")
        self.character_index = 0

    def get_next_character(self):
        c = self.f.read(1)
        self.character_index = self.f.tell()
        return c

    def revert(self, index: int):
        self.character_index = self.character_index - index
        self.f.seek(self.character_index)


class ScannerResult:

    def __init__(self):
        self.lexical_errors = []
        self.symbol_table = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'main']
        self.tokens = []
        self.line = 1

    def add(self, l, info):
        if len(l) >= self.line:
            l[self.line - 1] += f' {info}'
        else:
            l.append(info)

    def write_into_file(self):
        self.write(self.tokens, 'tokens.txt')
        self.write(self.lexical_errors, 'lexical_errors.txt', empty_message='There is no lexical error.')
        self.write(self.symbol_table, 'symbol_table.txt')

    def newLine(self):
        self.line += 1

    @classmethod
    def write(cls, output, file, empty_message=""):
        line = 1
        f = open(file, "w")
        if output:
            for item in output:
                f.writelines(f'{line}.\t{item} \n')
                line += 1
        else:
            f.write(empty_message)
        f.close()


class TokenType(Enum):
    ID, NUM, KEYWORD, UNKNOWN = range(3)


class State(Enum):
    START, ID, NUM, SYMBOL, COMMENT, END = range(3)


class Token:
    Type = TokenType.UNKNOWN
    content = ''

    def __repr__(self):
        return f'({self.Type} {self.content})'


def get_next_token(reader: Reader, result: ScannerResult):
    state = State.START
    token = Token()

    while state != State.END:
        c = reader.get_next_character()
        if c == '':  # EOF
            return False

        if state == State.START:
            if c.isalpha():
                pass
            elif c.isdigit():
                pass
            else:
                pass
        elif state == state.NUM:
            pass
        else:
            pass

    if token.Type == TokenType.ID:
        if token.content in KEYWORDS:
            token.Type = TokenType.KEYWORD

    return token.__repr__()



assert len(sys.argv) == 2
file_name = sys.argv[1]
r = Reader(file_name)
out = ScannerResult()
while get_next_token(r, out):
    pass
out.write_into_file()
