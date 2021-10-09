import sys
from enum import Enum

KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'main']
SYMBOLS = [';', ':', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '==', '<']
WHITESPACE = [' ', '\n', '\r', '\t', '\v', '\f']


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
    NUM, ID, KEYWORD, SYMBOL, COMMENT, ERROR, UNKNOWN = range(7)


class State(Enum):
    START, NUM, ID, SYMBOL, COMMENT, END = range(6)


class Token:
    type = TokenType.UNKNOWN
    content = ''

    def __repr__(self):
        return f'({self.type.name} {self.content})'


def get_next_token(reader: Reader, result: ScannerResult):
    state = State.START
    token = Token()

    while state != State.END:
        c = reader.get_next_character()
        if c in WHITESPACE or c == '':
            state = State.END
            continue

        token.content += c

        if state == State.START:
            if c.isalpha():
                state = State.ID
                token.type = TokenType.ID
            elif c.isdigit():
                state = State.NUM
                token.type = TokenType.NUM
            elif c in SYMBOLS:
                state = State.SYMBOL
                token.type = TokenType.SYMBOL
            elif c == '/':
                pass
            else:
                token.type = TokenType.ERROR

        elif state == state.NUM:
            if not c.isdigit():
                if c.isalpha():
                    pass  # todo error invalid number
                reader.revert(1)
                token.content = token.content[:-1]
                state = State.END

        elif state == state.ID:
            if not c.isalnum():
                reader.revert(1)
                token.content = token.content[:-1]
                state = State.END

        elif state == state.SYMBOL:
            if not token.content == '==':
                reader.revert(1)
                token.content = token.content[:-1]
                state = State.END

        elif state == state.COMMENT:
            pass

    if token.type == TokenType.ID:
        if token.content in KEYWORDS:
            token.type = TokenType.KEYWORD

    if token.type != TokenType.UNKNOWN:
        result.add(result.tokens, token.__repr__())

    if token.type == TokenType.ID and not result.symbol_table.__contains__(token.content):
        result.symbol_table.append(token.content)
    if c == '\n':
        result.newLine()
    return c != ''


assert len(sys.argv) == 2
file_name = sys.argv[1]
r = Reader(file_name)
out = ScannerResult()
while get_next_token(r, out):
    pass
out.write_into_file()
