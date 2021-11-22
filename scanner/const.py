from enum import Enum

KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']
SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '==', '<']
WHITESPACE = [' ', '\n', '\r', '\t', '\v', '\f']


class TokenType(Enum):
    NUM, ID, KEYWORD, SYMBOL, COMMENT, UNKNOWN, ERROR, END = range(8)


class State(Enum):
    START, NUM, ID, SYMBOL, ONE_LINE_COMMENT, MULTI_LINE_COMMENT, MULTI_LINE_COMMENT_END, UNDECIDED_COMMENT, END, ERROR = range(
        10)
