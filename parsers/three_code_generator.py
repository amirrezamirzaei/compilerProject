class Symbol:
    def __init__(self, name, kind=None, args_count=None, type=None, scope=None, address=None):
        self.name = name
        self.kind = kind
        self.args_count = args_count
        self.type = type
        self.scope = scope
        self.address = address

    def __str__(self):
        return f'name={self.name}\t\tkind={self.kind}\targs_count={self.args_count}\ttype={self.type}\tscope={self.scope}\taddress={self.address}'


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
        for symbol in self.symbol_table:
            print(symbol)
        print(self.symbol_stack)
        print('-------')
        p = self.symbol_stack.pop()
        self.stack_pointer.pop()
        for i in range(len(self.symbol_table)-p):
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
    RETURN_VALUE_ADDRESS = 5000
    STACK_POINTER_ADDRESS = 5004
    STACK_START_ADDRESS = 3000
    STACK_END_ADDRESS = 5000

    def __init__(self):
        self.i = 1
        self.semantic_errors = []
        self.semantic_stack = []
        self.program_block = []
        self.function_address = []
        self.SymbolTable = SymbolTable()

    def semantic_action(self, action_symbol, current_token):
        if action_symbol == '#save':
            self.save()
        elif action_symbol == '#begin':
            self.begin()
        elif action_symbol == '#save_type':
            self.save_type(current_token)
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
        elif action_symbol == '#save_stack':
            self.save_stack()
        elif action_symbol == '#delete_scope':
            self.delete_scope()
        elif action_symbol == '#increase_func_arg':
            self.increase_func_arg()
        elif action_symbol == '#pop_semantic_stack':
            self.pop_semantic_stack()
        elif action_symbol == '#loop_break_jump':
            self.loop_break_jump()
        elif action_symbol == '#backpatch_if':
            self.backpatch_if()
        elif action_symbol == '#backpatch_else':
            self.backpatch_else()
        elif action_symbol == '#finish_if':
            self.finish_if()
        
        else:
            print(action_symbol)
            2/0

    def push(self, p):
        self.semantic_stack.append(p)

    def add_code_to_program_block(self, command, arg1, arg2='', arg3='', line=None):
        if line:
            self.program_block[line-1] = f'{line}   ({command}, {arg1}, {arg2}, {arg3})'
        else:
            self.program_block.append(f'{self.i}   ({command}, {arg1}, {arg2}, {arg3})')
            self.i += 1

    def save(self):
        self.push(self.i)
        self.add_code_to_program_block('', '')

    def begin(self):
        self.add_code_to_program_block('ASSIGN', arg1='#1', arg2=self.RETURN_VALUE_ADDRESS)
        self.add_code_to_program_block('ASSIGN', arg1=self.STACK_START_ADDRESS, arg2=self.STACK_POINTER_ADDRESS)

    def save_type(self, current_token):
        self.push(current_token.content)

    def create_symbol(self, current_token):
        self.SymbolTable.add(current_token.content, type=self.semantic_stack.pop())

    def func_start(self):
        func = self.SymbolTable.symbol_table[-1]
        func.kind = 'function'
        func.args_count = 0
        if func.name != 'main':
            self.function_address.append(self.i)
            self.add_code_to_program_block('', '')
            func.address = self.i
        else:
            func.address = self.i
            # adding jump to main at the beginning of every function
            for line in self.function_address:
                self.add_code_to_program_block('JP', arg1=self.i, line=line)

    def set_kind_to_var(self, current_token):
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.kind = 'var'

        if symbol.type == 'void':
            self.semantic_errors.append(f"#{current_token.line}: Semantic Error! Illegal type of void for '{symbol.name}'")

        symbol.address = self.SymbolTable.stack_pointer[-1]
        self.SymbolTable.stack_pointer[-1] += 4

    def set_kind_to_array(self, current_token):
        array_size = int(current_token.content)
        symbol = self.SymbolTable.symbol_table[-1]
        symbol.kind = 'array'

        if symbol.type == 'void':
            self.semantic_errors.append(f"#{current_token.line}: Semantic Error! Illegal type of void for '{symbol.name}'")

        symbol.address = self.SymbolTable.stack_pointer[-1]
        self.SymbolTable.stack_pointer[-1] += array_size * 4
    
    @staticmethod
    def check_bad_exp_type(exp_type):
        if "array" in exp_type:
            return 'Type mismatch in operands, Got array instead of int.'
        if "void_func_output" in exp_type:
            return 'void type function has no output.'
        if "function" in exp_type:
            return 'Type mismatch in operands. Got function instead of int.'
        return None

    def new_scope(self):
        self.SymbolTable.new_scope()

    def delete_scope(self):
        self.SymbolTable.delete_scope()

    def save_stack(self):
        self.SymbolTable.stack_pointer[-1] += 4

    def increase_func_arg(self):
        last_function = self.SymbolTable.get_last_function()
        last_function.args_count += 1
    
    def pop_semantic_stack(self):
        self.semantic_stack.pop()
    
    def loop_break_jump(self):
        temp = self.semantic_stack[-2] # -2 ya -1 ???
        self.add_code_to_program_block('JP', '@{}'.format(temp))
    
    def backpatch_if(self):
        #avalesh ye semantic error check lazem darim

        backpatch = self.semantic_stack[-2]
        exp_adr = self.semantic_stack[-3]

        self.program_block[backpatch] = "{}   (JPF, {}{}, {})".format(
            # ina ye stacke joda daran ke tosh type negah midare baraye semantic check
            backpatch + 1,
            "@" if "indirect" in exp_type else "",
            exp_adr,
            self.i
        )
    
    def backpatch_else(self):
        backpatch = self.semantic_stack[-1]
        self.program_block[backpatch] = "{}   (JP, {})".format(backpatch + 1, self.i)
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()
    
    def finish_if(self):
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

