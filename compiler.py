import sys
from enum import Enum

KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']
SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '==', '<']
WHITESPACE = [' ', '\n', '\r', '\t', '\v', '\f']
LINE = 1


class Reader:

    def __init__(self, file_name: str):
        self.f = open(file_name, "r")
        self.character_index = 0
        self.line = 0
        self.current_character = ''

    def get_next_character(self):
        c = self.f.read(1)
        if c == '\n':
            self.line += 1
        self.character_index = self.f.tell()
        self.current_character = c
        return c

    def revert_single_character(self):
        if self.current_character == '\n':
            self.line -= 1
        self.character_index = self.character_index - 1
        self.f.seek(self.character_index)

    def revert(self, index: int):
        self.character_index = self.character_index - index
        self.f.seek(self.character_index)


class ScannerResult:

    def __init__(self):
        self.lexical_errors = []
        self.symbol_table = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']
        self.tokens = []
        self.index = 0

    def add(self, l, token):
        if l and l[len(l) - 1][0].line == token.line:
            l[len(l) - 1].append(token)
        else:
            l.append([token])

    def write_into_file(self):
        self.write(self.tokens, 'tokens.txt')
        self.write(self.lexical_errors, 'lexical_errors.txt', empty_message='There is no lexical error.')
        self.write(self.symbol_table, 'symbol_table.txt', is_list=False)

    @classmethod
    def write(cls, output, file, empty_message="", is_list=True):
        f = open(file, "w")
        if output:
            if is_list:
                for item in output:
                    out = ''
                    for token in item:
                        out += f'{token.__repr__()} '
                    f.writelines(f'{item[0].line}.\t{out}\n')
            else:
                for num, item in enumerate(output, 1):
                    f.writelines(f'{num}.\t{item}\n')
        else:
            f.write(empty_message)
        f.close()


class TokenType(Enum):
    NUM, ID, KEYWORD, SYMBOL, COMMENT, UNKNOWN, ERROR = range(7)


class State(Enum):
    START, NUM, ID, SYMBOL, ONE_LINE_COMMENT, MULTI_LINE_COMMENT, END, ERROR = range(8)


class Token:

    def __init__(self):
        self.type = TokenType.UNKNOWN
        self.content = ''
        self.error = ''
        self.line = LINE

    def __repr__(self):
        if self.type != TokenType.ERROR:
            return f'({self.type.name}, {self.content})'
        else:
            return f'({self.content}, {self.error})'


def is_accepted_character(c):
    return c.isalnum() or c in SYMBOLS or c in WHITESPACE

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
                token.error = 'Invalid input'
                state = state.END

        elif state == State.NUM:
            if not c.isdigit():
                if c.isalpha():
                    state = State.END
                    token.type = TokenType.ERROR
                    token.error = 'Invalid number'
                else:
                    reader.revert_single_character()
                    token.content = token.content[:-1]
                    state = State.END

        elif state == State.ID:
            if not c.isalnum() and is_accepted_character(c):
                reader.revert_single_character()
                token.content = token.content[:-1]
                state = state.END
            elif not is_accepted_character(c):
                token.type = TokenType.ERROR
                token.error = 'Invalid input'
                state = state.END

        elif state == State.SYMBOL:
            if not token.content == '==':
                reader.revert_single_character()
                token.content = token.content[:-1]
                state = State.END

        elif state == State.ONE_LINE_COMMENT:
            pass

        elif state == State.MULTI_LINE_COMMENT:
            pass

    if token.type == TokenType.ID:
        if token.content in KEYWORDS:
            token.type = TokenType.KEYWORD

    if token.type != TokenType.ERROR and token.type != TokenType.UNKNOWN:
        result.add(result.tokens, token)
    elif token.type == TokenType.ERROR:
        result.add(result.lexical_errors, token)

    if token.type == TokenType.ID and not result.symbol_table.__contains__(token.content):
        result.symbol_table.append(token.content)

    if c == '\n':
        global LINE
        LINE += 1

    return c != ''


file_name = sys.argv[1]
r = Reader(file_name)
out = ScannerResult()
while get_next_token(r, out):
    pass
out.write_into_file()
