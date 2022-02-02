DEBUG = False


class Symbol:
    def __init__(self, name, kind=None, args_count=None, type=None, scope=None, address=None):
        self.name = name
        self.kind = kind  # function/var/array/reference
        self.args_count = args_count
        self.type = type
        self.scope = scope
        self.address = address
        self.reference = False

    def __str__(self):
        return f'name={self.name}\t\tkind={self.kind}\targs_count={self.args_count}\ttype={self.type}\tscope={self.scope}\taddress={self.address} reference={self.reference}'


class SymbolType:
    # kind = var or array
    # address = direct or indirect
    def __init__(self, kind, address):
        self.kind = kind
        self.address = address

    def __str__(self):
        return f'{self.kind} {self.address}'


class SymbolTable:

    def __init__(self):
        self.symbol_table = []
        self.symbol_stack = [0]
        self.data_pointer = 3000

    def add(self, name, kind=None, type=None):
        if name == 'fact':
            raise ValueError(f'recursive escape')
        symbol = Symbol(name, kind=kind, scope=len(self.symbol_stack), type=type)
        self.symbol_table.append(symbol)
        if kind == 'function':
            self.new_scope()

    def new_scope(self):
        self.symbol_stack.append(len(self.symbol_table))

    def delete_scope(self):
        self.symbol_stack.pop()

    def get_last_function(self):
        for symbol in reversed(self.symbol_table):
            if symbol.kind == 'function':
                return symbol

    def get_last_var(self):
        for symbol in reversed(self.symbol_table):
            if symbol.kind == 'var':
                return symbol

    def get_function_args(self, func_symbol):
        args = []
        for symbol in reversed(self.symbol_table):
            if symbol.name == func_symbol.name and symbol.kind == 'function':
                break
            if symbol.kind == 'function':
                args = []
            else:
                args.append(symbol)
        return args[-func_symbol.args_count:]


class ThreeCodeGenerator:
    RETURN_ADDRESS_REGISTER = 8000
    RETURN_VALUE_REGISTER = 8004
    last_temp_address = 9000

    def __init__(self):
        self.i = 0
        self.semantic_errors = []
        self.semantic_stack = []
        self.program_block = []
        self.function_jump_stack = []
        self.repeat_stack = []
        self.break_stack = []
        self.main_return_stack = []

        self.function_to_be_called = []
        self.function_args = []
        self.function_pushed_args = []
        self.SymbolTable = SymbolTable()

        self.function_not_found_error = False

    def semantic_action(self, action_symbol, current_token):
        # print(action_symbol, self.semantic_stack, self.function_to_be_called)
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
        elif action_symbol == '#new_scope':
            self.new_scope()
        elif action_symbol == '#end_func_scope':
            self.end_func_scope()
        elif action_symbol == '#increase_func_arg':
            self.increase_func_arg()
        elif action_symbol == '#set_kind_to_reference':
            self.set_kind_to_reference(current_token)
        elif action_symbol == '#pop_semantic_stack':
            self.pop_semantic_stack()
        elif action_symbol == '#break_repeat':
            self.break_repeat(current_token)
        elif action_symbol == '#save':
            self.save()
        elif action_symbol == '#jpf_if':
            self.jpf_if()
        elif action_symbol == '#jpf_save_if':
            self.jpf_save_if(current_token)
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
        elif action_symbol == '#pid':
            self.pid(current_token)
        elif action_symbol == '#assign':
            self.assign(current_token)
        elif action_symbol == '#get_array_cell_address':
            self.get_array_cell_address()
        elif action_symbol == '#operation':
            self.operation(current_token)
        elif action_symbol == '#multiply':
            self.operation(current_token, mult=True)
        elif action_symbol == '#save_num':
            self.save_num(current_token)
        elif action_symbol == '#start_function':
            self.start_function()
        elif action_symbol == '#call_func':
            self.call_func(current_token)
        elif action_symbol == '#add_arg':
            self.add_arg()
        else:
            raise ValueError(f'invalid action symbol: {action_symbol}')

    def get_temp_address(self):
        address = self.last_temp_address
        self.last_temp_address += 4
        return address

    def push(self, p):
        self.semantic_stack.append(p)

    def new_scope(self):
        self.SymbolTable.new_scope()

    def add_code_to_program_block(self, command, arg1, arg2='', arg3='', line=None, debug=''):
        if not DEBUG:
            debug = ''
        if line:
            self.program_block[line] = f'{line}\t({command}, {arg1}, {arg2}, {arg3}){debug}'
        else:
            self.program_block.append(f'{self.i}\t({command}, {arg1}, {arg2}, {arg3}){debug}')
            self.i += 1

    def begin(self):
        self.add_code_to_program_block('ASSIGN', arg1='#1', arg2=self.RETURN_VALUE_REGISTER, debug='#begin')
        self.add_code_to_program_block('ASSIGN', arg1='#1', arg2=self.RETURN_ADDRESS_REGISTER, debug='#begin')

    def end(self):
        for line in self.main_return_stack:
            self.add_code_to_program_block('JP', arg1=self.i, line=line, debug='#return')
        self.main_return_stack = []
        self.add_code_to_program_block('ASSIGN', arg1='#6000', arg2='3000', debug='#END')
        print('end', self.semantic_stack)

    def create_symbol(self, current_token):
        # we don't know the kind(var,array,function,reference) of the symbol yet
        self.SymbolTable.add(current_token.content, type=self.semantic_stack.pop())

    def func_start(self):
        func = self.SymbolTable.symbol_table[-1]
        func.kind = 'function'
        func.args_count = 0
        if func.name != 'main':
            func.address = self.i + 1
            self.function_jump_stack.append(self.i)
            self.add_code_to_program_block('', '', debug='#func_start')
        else:
            func.address = self.i
            # adding jump to main at the beginning of every function
            for line in self.function_jump_stack:
                self.add_code_to_program_block('JP', arg1=self.i, line=line, debug='#func_start')

    def set_kind_to_var(self, current_token):
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.kind = 'var'

        if symbol.type == 'void':
            self.semantic_errors.append(
                f"#{current_token.line} : Semantic Error! Illegal type of void for '{symbol.name}'.")

        symbol.address = self.SymbolTable.data_pointer
        self.SymbolTable.data_pointer += 4

    def set_kind_to_array(self, current_token):
        array_size = int(current_token.content)
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.kind = 'array'

        if symbol.type == 'void':
            self.semantic_errors.append(
                f"#{current_token.line} : Semantic Error! Illegal type of void for '{symbol.name}'.")

        symbol.address = self.SymbolTable.data_pointer
        self.SymbolTable.data_pointer += array_size * 4

    def set_kind_to_reference(self, current_token):
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.reference = True
        symbol.kind = 'array'

        if symbol.type == 'void':
            self.semantic_errors.append(
                f"#{current_token.line} : Semantic Error! Illegal type of void for '{symbol.name}'.")

    def end_func_scope(self):
        func = self.SymbolTable.get_last_function()
        # jump to caller at the end of functions
        if func.name != 'main':
            self.add_code_to_program_block('JP', arg1=f'@{self.RETURN_ADDRESS_REGISTER}', debug='#end_func_scope')
        self.SymbolTable.delete_scope()

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
                f"#{current_token.line} : Semantic Error! No 'repeat ... until' found for 'break'.")

    def save(self):
        self.push(self.i)
        self.add_code_to_program_block('', '', debug='#save')

    def jpf_if(self):
        line = self.semantic_stack.pop()
        exp, type = self.semantic_stack.pop()
        if type.address == 'indirect':
            exp = f'@{exp}'
        self.add_code_to_program_block('JPF', arg1=exp, arg2=self.i, line=line, debug='#jpf_if')

    def jpf_save_if(self, current_token):
        line = self.semantic_stack.pop()
        exp, type = self.semantic_stack.pop()
        if type.address == 'indirect':
            exp = f'@{exp}'
        self.add_code_to_program_block('JPF', arg1=exp, arg2=self.i + 1, line=line, debug='#jpf_save_if')
        self.save()

    def jp_if(self):
        line = self.semantic_stack.pop()
        self.add_code_to_program_block('JP', arg1=self.i, line=line, debug='#jp_if')

    def repeat_start(self):
        self.repeat_stack.append(self.i)

    def until(self):
        exp, type = self.semantic_stack.pop()
        line = self.repeat_stack.pop()
        if type.address == 'indirect':
            exp = f'@{exp}'
        self.add_code_to_program_block('JPF', arg1=exp, arg2=line, debug='#until')

        for break_line in self.break_stack:
            self.add_code_to_program_block('JP', arg1=self.i, line=break_line)
        self.break_stack = []

    def return_void(self):
        func = self.SymbolTable.get_last_function()
        if func.name == 'main':
            self.main_return_stack.append(self.i)
            self.add_code_to_program_block('', '')  # go to last line of code
        else:
            self.add_code_to_program_block('JP', arg1=f'@{self.RETURN_ADDRESS_REGISTER}', debug='#return_void')

    def return_exp(self):
        arg, type = self.semantic_stack.pop()
        if type.address == 'indirect':
            arg = f'@{arg}'
        self.add_code_to_program_block('ASSIGN', arg1=arg, arg2=self.RETURN_VALUE_REGISTER,
                                       debug='#setting_return_value')
        self.add_code_to_program_block('JP', arg1=f'@{self.RETURN_ADDRESS_REGISTER}', debug='#return_void')

    def pid(self, current_token):
        if current_token.content == 'output':
            self.push(('output', 'function', None))
        else:
            scope = len(self.SymbolTable.symbol_stack)
            flag = True
            for symbol in reversed(self.SymbolTable.symbol_table):
                if (symbol.scope == scope and flag) or symbol.scope == 1:
                    if symbol.name == current_token.content:
                        if symbol.kind == 'var' or symbol.kind == 'array':
                            t = self.get_temp_address()
                            self.add_code_to_program_block('ASSIGN', arg1=f'#{symbol.address}', arg2=t, debug='#pid')
                            if symbol.reference:  # todo check shavad
                                self.add_code_to_program_block('ASSIGN', arg1=f'@{t}', arg2=t, debug='#pid')
                            self.push((t, SymbolType(symbol.kind, 'indirect')))
                        elif symbol.kind == 'function':
                            self.push((symbol.address, 'function', symbol))
                        return
                    flag = (symbol.kind != 'function')

            self.semantic_errors.append(
                f"#{current_token.line} : Semantic Error! '{current_token.content}' is not defined.")
            self.push((6000, SymbolType('var', 'direct')))  # fake push so we dont get any error

    def assign(self, current_token):
        arg1, type1 = self.semantic_stack.pop()
        arg2, type2 = self.semantic_stack.pop()
        if type1.address == 'indirect':
            arg1 = f'@{arg1}'
        if type2.address == 'indirect':
            arg2 = f'@{arg2}'
        self.add_code_to_program_block('ASSIGN', arg1=arg1, arg2=arg2, debug='#assign')
        self.push((f'{arg2}'.replace('@', ''), type2))

    def get_array_cell_address(self):
        arg1, type1 = self.semantic_stack.pop()
        arg2, type2 = self.semantic_stack.pop()
        if type1.address == 'indirect':
            arg1 = f'@{arg1}'
        t = self.get_temp_address()
        self.add_code_to_program_block('MULT', arg1=arg1, arg2='#4', arg3=t, debug='#array_cell')
        self.add_code_to_program_block('ADD', arg1=arg2, arg2=t, arg3=t, debug='#array_cell')
        # todo fix
        self.push((t, SymbolType('var', 'indirect')))

    def operation(self, current_token, mult=False):
        arg1, type1 = self.semantic_stack.pop()
        op = '*' if mult else self.semantic_stack.pop()
        arg2, type2 = self.semantic_stack.pop()
        if type1.kind != type2.kind:
            self.semantic_errors.append(
                f"#{current_token.line} : Semantic Error! Type mismatch in operands, Got array instead of int.")
            self.push((6000, SymbolType('var', 'direct')))
            return
        if op == '*':
            op = 'MULT'
        elif op == '+':
            op = 'ADD'
        elif op == '-':
            op = 'SUB'
            arg1, type1, arg2, type2 = arg2, type2, arg1, type1
        elif op == '==':
            op = 'EQ'
        elif op == '<':
            op = 'LT'
            arg1, type1, arg2, type2 = arg2, type2, arg1, type1
        if type1.address == 'indirect':
            arg1 = f'@{arg1}'
        if type2.address == 'indirect':
            arg2 = f'@{arg2}'
        t = self.get_temp_address()
        self.add_code_to_program_block(op, arg1=arg1, arg2=arg2, arg3=t)
        self.push((t, SymbolType('var', 'direct')))

    def save_num(self, current_token):
        t = self.get_temp_address()
        self.add_code_to_program_block('ASSIGN', arg1=f'#{current_token.content}', arg2=t, debug='#save_num')
        self.push((t, SymbolType('var', 'direct')))

    def start_function(self):
        p = self.semantic_stack.pop()
        if len(p) != 3:
            self.function_not_found_error = True
            print('ERROR FUNCTION NOT FOUND')
            return
        self.function_not_found_error = False
        address, _, symbol = p

        if address == 'output':
            print(f'starting function output')
            self.function_to_be_called.append('output')
        else:
            print(f'starting function {symbol.name}')
            self.function_to_be_called.append(symbol)

    def call_func(self, current_token):
        list_errors = []
        if self.function_not_found_error:
            self.push((6000, SymbolType('var', 'direct')))  # fake push so we don't get any error
            self.function_args = []
            return
        if self.function_to_be_called[-1] == 'output':
            if len(self.function_args) != 1:
                self.semantic_errors.append(
                    f"#{current_token.line} : Semantic Error! Mismatch in numbers of arguments of 'output'.")
                self.push((6000, SymbolType('var', 'direct')))  # fake push so we don't get any error
                self.function_args = []
                return
            arg, type = self.function_args.pop()
            if type.address == 'indirect':
                arg = f'@{arg}'
            self.add_code_to_program_block('PRINT', arg1=arg)
            self.push('NULL')

        else:
            if len(self.function_args) != self.function_to_be_called[-1].args_count:
                self.semantic_errors.append(
                    f"#{current_token.line} : Semantic Error! Mismatch in numbers of arguments of '{self.function_to_be_called[-1].name}'.")
                self.push((6000, SymbolType('var', 'direct')))  # fake push so we don't get any error
                self.function_args = []
                return

            for num, symbol in enumerate(self.SymbolTable.get_function_args(self.function_to_be_called[-1])):
                arg, type = self.function_args.pop()
                if symbol.kind != type.kind:
                    list_errors.append(
                        f"#{current_token.line} : Semantic Error! Mismatch in type of argument "
                        f"{self.function_to_be_called[-1].args_count-num} of '{self.function_to_be_called[-1].name}'."
                        f" Expected '{symbol.kind.replace('var','int')}' but got '{type.kind.replace('var','int')}' instead.")
                    continue
                if symbol.reference:
                    print(arg, type)
                    type.address = 'direct'
                if type.address == 'indirect':
                    arg = f'@{arg}'
                self.add_code_to_program_block('ASSIGN', arg1=arg, arg2=symbol.address, debug='#call_func')
            saved_return_address = self.get_temp_address()
            self.add_code_to_program_block('ASSIGN', arg1=self.RETURN_ADDRESS_REGISTER, arg2=saved_return_address)
            self.add_code_to_program_block('ASSIGN', arg1=f'#{self.i + 2}', arg2=self.RETURN_ADDRESS_REGISTER,
                                           debug='#call_func')
            self.add_code_to_program_block('JP', arg1=self.function_to_be_called[-1].address, debug='#call_func')
            self.add_code_to_program_block('ASSIGN', arg1=saved_return_address, arg2=self.RETURN_ADDRESS_REGISTER)
            t = self.get_temp_address()
            # setting return address
            self.add_code_to_program_block('ASSIGN', arg1=self.RETURN_VALUE_REGISTER, arg2=t, debug='#call_func')
            self.push((t, SymbolType('var', 'direct')))
        self.function_to_be_called.pop()

        self.semantic_errors += reversed(list_errors)

    def add_arg(self):
        if self.function_not_found_error:
            return
        self.function_args.append(self.semantic_stack.pop())
