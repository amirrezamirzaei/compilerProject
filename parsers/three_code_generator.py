DEBUG = False

class Symbol:
    def __init__(self, name, kind=None, args_count=None, type=None, scope=None, address=None):
        self.name = name
        self.kind = kind
        self.args_count = args_count
        self.type = type
        self.scope = scope
        self.address = address
        self.reference = False

    def __str__(self):
        return f'name={self.name}\t\tkind={self.kind}\targs_count={self.args_count}\ttype={self.type}\tscope={self.scope}\taddress={self.address}\treference={self.reference}'


class SymbolTable:

    def __init__(self):
        self.symbol_table = []
        self.symbol_stack = [0]
        self.stack_pointer = [-2000]

    def add(self, name, kind=None, type=None):
        symbol = Symbol(name, kind=kind, scope=len(self.symbol_stack), type=type)
        self.symbol_table.append(symbol)
        if kind == 'function':
            self.new_scope()

    def new_scope(self):
        self.symbol_stack.append(len(self.symbol_table))
        self.stack_pointer.append(-2000)

    def delete_scope(self):
        p = self.symbol_stack.pop()
        self.stack_pointer.pop()
        for i in range(len(self.symbol_table) - p):
            self.symbol_table.pop()

    def get_last_function(self):
        for symbol in reversed(self.symbol_table):
            if symbol.kind == 'function':
                return symbol

    def get_last_var(self):
        for symbol in reversed(self.symbol_table):
            if symbol.kind == 'var':
                return symbol


class ThreeCodeGenerator:
    RETURN_REGISTER = 6000
    STACK_POINTER_ADDRESS = 6004

    STACK_START_ADDRESS = 5000
    STACK_END_ADDRESS = 7000
    STACK_BLOCK_SIZE = 2000

    last_temp_address = 2004

    def __init__(self):
        self.i = 1
        self.semantic_errors = []
        self.semantic_stack = []
        self.program_block = []
        self.function_address = []
        self.repeat_stack = []
        self.break_stack = []
        self.main_return_stack = []
        self.SymbolTable = SymbolTable()

    def semantic_action(self, action_symbol, current_token):
        if action_symbol == '#begin':
            self.begin()
        elif action_symbol == '#end':
            self.end()
        elif action_symbol == '#push':
            self.push(current_token.content)
        elif action_symbol == '#create_symbol':
            self.create_symbol(current_token)
        elif action_symbol == '#func_start':
            self.func_start()
        elif action_symbol == '#set_kind_to_var':
            self.set_kind_to_var(current_token)
        elif action_symbol == '#set_kind_to_array':
            self.set_kind_to_array(current_token)
        elif action_symbol == '#set_kind_to_reference':
            self.set_kind_to_reference(current_token)
        elif action_symbol == '#new_scope':
            self.new_scope()
        elif action_symbol == '#function_start_space':
            self.function_start_space()
        elif action_symbol == '#end_func_scope':
            self.end_func_scope()
        elif action_symbol == '#increase_func_arg':
            self.increase_func_arg()
        elif action_symbol == '#pop_semantic_stack':
            self.pop_semantic_stack()
        elif action_symbol == '#pid':
            self.pid(current_token)
        elif action_symbol == '#assign':
            self.assign(current_token)
        elif action_symbol == '#save_num':
            self.save_num(current_token)
        elif action_symbol == '#operation':
            self.operation()
        elif action_symbol == '#multiply':
            self.operation(mult=True)
        elif action_symbol == '#break_repeat':
            self.break_repeat(current_token)
        elif action_symbol == '#save':
            self.save()
        elif action_symbol == '#jpf_if':
            self.jpf_if()
        elif action_symbol == '#jpf_save_if':
            self.jpf_save_if()
        elif action_symbol == '#jp_if':
            self.jp_if()
        elif action_symbol == '#repeat_start':
            self.repeat_start()
        elif action_symbol == '#until':
            self.until()
        elif action_symbol == '#return_void':
            self.return_void()
        elif action_symbol == '#return_exp':
            self.return_exp()
        elif action_symbol == '#get_array_cell_address':
            self.get_array_cell_address()
        else:
            print(action_symbol)
            2 / 0

    def get_temp_address(self):
        address = self.last_temp_address
        self.last_temp_address += 4
        return address

    def push(self, p):
        self.semantic_stack.append(p)

    def add_code_to_program_block(self, command, arg1, arg2='', arg3='', line=None, debug=''):
        if not DEBUG:
            debug = ''
        if line:
            self.program_block[line - 1] = f'{line}   ({command}, {arg1}, {arg2}, {arg3}){debug}'
        else:
            self.program_block.append(f'{self.i}   ({command}, {arg1}, {arg2}, {arg3}){debug}')
            self.i += 1

    def save(self):
        self.push(self.i)
        self.add_code_to_program_block('', '', debug='#save')

    def begin(self):
        self.add_code_to_program_block('ASSIGN', arg1='#1', arg2=self.RETURN_REGISTER, debug='#begin')
        self.add_code_to_program_block('ASSIGN', arg1=f'#{self.STACK_START_ADDRESS}', arg2=self.STACK_POINTER_ADDRESS,
                                       debug='#begin')

    def create_symbol(self, current_token):
        # we don't know the kind(var,array,function,reference) of the symbol yet
        self.SymbolTable.add(current_token.content, type=self.semantic_stack.pop())

    def func_start(self):
        func = self.SymbolTable.symbol_table[-1]
        func.kind = 'function'
        func.address = self.i
        func.args_count = 0
        if func.name != 'main':
            self.function_address.append(self.i)
            self.add_code_to_program_block('', '', debug='#func_start')
        else:
            # adding jump to main at the beginning of every function
            for line in self.function_address:
                self.add_code_to_program_block('JP', arg1=self.i, line=line, debug='#func_start')

    def set_kind_to_var(self, current_token):
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.kind = 'var'

        if symbol.type == 'void':
            self.semantic_errors.append(
                f"#{current_token.line}: Semantic Error! Illegal type of void for '{symbol.name}'")

        symbol.address = self.SymbolTable.stack_pointer[-1]
        self.SymbolTable.stack_pointer[-1] += 4

    def set_kind_to_array(self, current_token):
        array_size = int(current_token.content)
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.kind = 'array'

        if symbol.type == 'void':
            self.semantic_errors.append(
                f"#{current_token.line}: Semantic Error! Illegal type of void for '{symbol.name}'")

        symbol.address = self.SymbolTable.stack_pointer[-1]
        self.SymbolTable.stack_pointer[-1] += array_size * 4

    def set_kind_to_reference(self, current_token):
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.kind = 'array'
        symbol.reference = True

        if symbol.type == 'void':
            self.semantic_errors.append(
                f"#{current_token.line}: Semantic Error! Illegal type of void for '{symbol.name}'")

    def new_scope(self):
        self.SymbolTable.new_scope()

    def end_func_scope(self):
        # todo check
        func = self.SymbolTable.get_last_function()
        # jump to caller at the end of functions
        if func.name != 'main':
            offset = -self.STACK_BLOCK_SIZE + func.args_count * 4
            t = self.get_temp_address()
            self.add_code_to_program_block('ASSIGN', arg1=self.STACK_POINTER_ADDRESS, arg2=t,
                                           debug='#end_func_scope')
            self.add_code_to_program_block('ADD', arg1=t, arg2=f'#{offset}', arg3=t, debug='#end_func_scope')
            self.add_code_to_program_block('ASSIGN', arg1=f'@{t}', arg2=t, debug='#end_func_scope')
            self.add_code_to_program_block('JP', arg1=t, debug='#end_func_scope')
            self.SymbolTable.delete_scope()

    def end(self):
        # todo remove after debug
        for line in self.main_return_stack:
            self.add_code_to_program_block('JP', arg1=self.i, line=line, debug='#return')
        self.main_return_stack = []
        self.add_code_to_program_block('ASSIGN', arg1='6000', arg2='6000', debug='#END')
        print(self.semantic_stack)

    def function_start_space(self):
        # setting two space aside for return value and return address
        self.SymbolTable.stack_pointer[-1] += 2 * 4

    def increase_func_arg(self):
        last_function = self.SymbolTable.get_last_function()
        last_function.args_count += 1

    def pop_semantic_stack(self):
        return self.semantic_stack.pop()

    def break_repeat(self, current_token):
        if self.repeat_stack:
            self.break_stack.append(self.i)
            self.add_code_to_program_block('', '', debug='#break_repeat')
        else:
            self.semantic_errors.append(
                f"#{current_token.line}: Semantic Error! No 'repeat ... until' found for 'break'")

    def jpf_if(self):
        line = self.semantic_stack.pop()
        exp, type = self.semantic_stack.pop()
        if type == 'indirect':
            exp = f'@{exp}'
        self.add_code_to_program_block('JPF', arg1=exp, arg2=self.i, line=line, debug='#jpf_if')

    def jpf_save_if(self):
        line = self.semantic_stack.pop()
        exp, type = self.semantic_stack.pop()
        if type == 'indirect':
            exp = f'@{exp}'
        self.add_code_to_program_block('JPF', arg1=exp, arg2=self.i + 1, line=line, debug='#jpf_save_if')
        self.semantic_stack.append(self.i)
        self.save()

    def jp_if(self):
        line = self.semantic_stack.pop()
        self.add_code_to_program_block('JP', arg1=self.i, line=line, debug='#jp_if')

    def repeat_start(self):
        self.repeat_stack.append(self.i)

    def until(self):
        exp, type = self.semantic_stack.pop()
        line = self.repeat_stack.pop()
        if type == 'indirect':
            exp = f'@{exp}'
        self.add_code_to_program_block('JPF', arg1=exp, arg2=line, debug='#until')

        for break_line in self.break_stack:
            self.add_code_to_program_block('JP', arg1=self.i, line=break_line)
        self.break_stack = []

    def return_void(self):
        func = self.SymbolTable.get_last_function()
        if func.name == 'main':
            self.main_return_stack.append(self.i)
            self.add_code_to_program_block('', '')
        else:
            offset = -self.STACK_BLOCK_SIZE + func.args_count * 4
            t = self.get_temp_address()
            self.add_code_to_program_block('ASSIGN', arg1=self.STACK_POINTER_ADDRESS, arg2=t, debug='#return_void')
            self.add_code_to_program_block('ADD', arg1=t, arg2=f'#{offset}', arg3=t, debug='#return_void')
            self.add_code_to_program_block('ASSIGN', arg1=f'@{t}', arg2=t, debug='#return_void')
            self.add_code_to_program_block('JP', arg1=f'@{t}', debug='#return_void')

    def return_exp(self):
        arg, type = self.semantic_stack.pop()
        if type == 'indirect':
            arg = f'@{arg}'
        func = self.SymbolTable.get_last_function()
        self.add_code_to_program_block('ASSIGN', arg1=arg, arg2=self.RETURN_REGISTER, debug='#setting_return_value')
        offset = -self.STACK_BLOCK_SIZE + func.args_count * 4
        t = self.get_temp_address()
        self.add_code_to_program_block('ASSIGN', arg1=self.STACK_POINTER_ADDRESS, arg2=t, debug='#return_void')
        self.add_code_to_program_block('ADD', arg1=t, arg2=f'#{offset}', arg3=t, debug='#return_void')
        self.add_code_to_program_block('ASSIGN', arg1=f'@{t}', arg2=t, debug='#return_void')
        self.add_code_to_program_block('JP', arg1=f'@{t}', debug='#return_void')

    def pid(self, current_token):
        if current_token.content == 'output':
            self.push('output')
        else:
            for symbol in reversed(self.SymbolTable.symbol_table):
                if symbol.name == current_token.content:
                    t = self.get_temp_address()
                    if symbol.kind == 'var' or symbol.kind == 'array':
                        self.add_code_to_program_block('ASSIGN', arg1=self.STACK_POINTER_ADDRESS, arg2=t, debug='#pid')
                        self.add_code_to_program_block('ADD', arg1=t, arg2=f'#{symbol.address}', arg3=t, debug='#pid')
                        if symbol.reference:
                            self.add_code_to_program_block('ASSIGN', arg1=f'@{t}', arg2=t, debug='#pid')
                        self.push((t, 'indirect'))
                    elif symbol.kind == 'function':
                        self.push((symbol.address, 'function'))
                    return
            self.semantic_errors.append(
                f"#{current_token.line}: Semantic Error! '{current_token.content}' is not defined'")

    def assign(self, current_token):
        print('assign', self.semantic_stack)
        arg1, type1 = self.semantic_stack.pop()
        arg2, type2 = self.semantic_stack.pop()
        # self.push((arg2, type2)) todo check this
        if type1 == 'indirect':
            arg1 = f'@{arg1}'
        if type2 == 'indirect':
            arg2 = f'@{arg2}'
        self.add_code_to_program_block('ASSIGN', arg1=arg1, arg2=arg2, debug='#assign')
        self.push((arg2.replace('@',''), type2))

    def get_array_cell_address(self):
        arg1, type1 = self.semantic_stack.pop()
        arg2, type2 = self.semantic_stack.pop()
        if type1 == 'indirect':
            arg1 = f'@{arg1}'
        t = self.get_temp_address()
        self.add_code_to_program_block('MULT', arg1=arg1, arg2='#4', arg3=t, debug='#array_cell')
        self.add_code_to_program_block('ADD', arg1=arg2, arg2=t, arg3=t, debug='#array_cell')
        self.push((t, 'indirect'))

    def save_num(self, current_token):
        t = self.get_temp_address()
        self.add_code_to_program_block('ASSIGN', arg1=f'#{current_token.content}', arg2=t, debug='#save_num')
        self.push((t, 'direct'))

    def operation(self, mult=False):
        arg1, type1 = self.semantic_stack.pop()
        op = '*' if mult else self.semantic_stack.pop()
        arg2, type2 = self.semantic_stack.pop()
        if op == '*':
            op = 'MULT'
        elif op == '+':
            op = 'ADD'
        elif op == '-':
            op = 'SUB'
        elif op == '==':
            op = 'EQ'
        elif op == '<':
            op = 'LT'
        if type1 == 'indirect':
            arg1 = f'@{arg1}'
        if type2 == 'indirect':
            arg2 = f'@{arg2}'
        t = self.get_temp_address()
        self.add_code_to_program_block(op, arg1=arg1, arg2=arg2, arg3=t)
        self.push((t, 'direct'))
