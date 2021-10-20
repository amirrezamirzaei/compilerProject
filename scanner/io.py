class Reader:

    def __init__(self, file_name: str):
        f = open(file_name, "r")
        self.code = f.read()
        self.index = 0
        f.close()
        self.current_character = ''
        self.line = 1

    def get_next_character(self):
        if len(self.code) <= self.index:
            return ''
        c = self.code[self.index]
        self.index += 1
        self.current_character = c
        if c == '\n':
            self.line += 1
        return c

    def revert_single_character(self):
        if self.current_character == '\n':
            self.line -= 1
        self.index -= 1


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
