from scanner.const import *
from scanner.io import *


class Token:

    def __init__(self, line):
        self.type = TokenType.UNKNOWN
        self.content = ''
        self.error = ''
        self.line = line

    def __repr__(self):
        if self.type != TokenType.ERROR:
            return f'({self.type.name}, {self.content})'
        else:
            if self.error == 'Unclosed comment' and len(self.error) > 7:
                return f'({self.content.strip()[0:7]}..., {self.error})'
            return f'({self.content.strip()}, {self.error})'


def is_accepted_character(c):
    return c.isalnum() or c in SYMBOLS or c in WHITESPACE or c == '/'


def get_next_token(reader: Reader, result: ScannerResult):
    state = State.START
    token = Token(reader.line)

    while state != State.END:
        c = reader.get_next_character()

        if (c in WHITESPACE and token.type != TokenType.COMMENT) or c == '':
            if (state == State.ONE_LINE_COMMENT or state == State.MULTI_LINE_COMMENT or state == State.MULTI_LINE_COMMENT_END) and c == '' and state != State.ONE_LINE_COMMENT:
                token.type = TokenType.ERROR
                token.error = 'Unclosed comment'
            if state == State.UNDECIDED_COMMENT:
                token.type = TokenType.ERROR
                token.error = 'Invalid input'
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
                state = State.SYMBOL if c == '=' or c == '*' else State.END  # symbols that need lookahead
                token.type = TokenType.SYMBOL
            elif c == '/':
                state = State.UNDECIDED_COMMENT
                token.type = TokenType.COMMENT
            else:
                token.type = TokenType.ERROR
                token.error = 'Invalid input'
                state = State.END

        elif state == State.NUM:
            if not c.isdigit():
                if c.isalpha() or not is_accepted_character(c):
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
                state = State.END
            elif not is_accepted_character(c):
                token.type = TokenType.ERROR
                token.error = 'Invalid input'
                state = State.END

        elif state == State.SYMBOL:
            if token.content == '*/' or not is_accepted_character(c):
                token.type = TokenType.ERROR
                token.error = 'Invalid input'
                state = State.END
            elif not token.content == '==' and is_accepted_character(c):
                reader.revert_single_character()
                token.content = token.content[:-1]
                state = State.END

        elif state == State.UNDECIDED_COMMENT:
            if c == '/':
                state = State.ONE_LINE_COMMENT
            elif c == '*':
                state = State.MULTI_LINE_COMMENT
            else:
                token.type = TokenType.ERROR
                token.error = 'Invalid input'
                if is_accepted_character(c):  # if the character after / is an invalid character we should output it
                    # as an error
                    reader.revert_single_character()
                    token.content = token.content[:-1]
                state = State.END


        elif state == State.ONE_LINE_COMMENT:
            if c == '\n':
                state = State.END

        elif state == State.MULTI_LINE_COMMENT:
            if c == '*':
                state = State.MULTI_LINE_COMMENT_END


        elif state == State.MULTI_LINE_COMMENT_END:
            if c == '/':
                state = State.END
            elif c != '*':
                state = State.MULTI_LINE_COMMENT

    if token.type == TokenType.ID:
        if token.content in KEYWORDS:
            token.type = TokenType.KEYWORD

    if not token.type in [TokenType.ERROR, TokenType.UNKNOWN, TokenType.COMMENT]:
        result.add(result.tokens, token)
    elif token.type == TokenType.ERROR:
        if token.content == '*/':
            token.error = 'Unmatched comment'
        result.add(result.lexical_errors, token)

    if token.type == TokenType.ID and not result.symbol_table.__contains__(token.content):
        result.symbol_table.append(token.content)

    if token.type == TokenType.COMMENT:
        return get_next_token(reader, result)

    return c != ''
