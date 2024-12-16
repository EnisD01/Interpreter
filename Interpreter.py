# Name: Enis Denizcier
# CISC 3160
# Interpreter.py
# 12-16-24

import re
from collections import defaultdict

# Tokenize the program into list of tokens
def tokenize(program):
    token_spec = [
        ('NUMBER',    r'\d+'),           # Integer literal
        ('IDENT',     r'[a-zA-Z_][a-zA-Z_0-9]*'),  # Identifier
        ('OP',        r'[+\-*/()]'),     # Operators and parentheses
        ('ASSIGN',    r'='),             # Assignment operator
        ('END',       r';'),             # End of statement
        ('SKIP',      r'[ \t]+'),       # Skip spaces and tabs
        ('MISMATCH',  r'.'),             # Any other character
    ]
    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_spec)
    for match in re.finditer(tok_regex, program):
        kind = match.lastgroup
        value = match.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character: {value}')
        yield (kind, value)

# Parse list of tokens into syntax tree
def parse(tokens):
    def expect(kind):
        nonlocal index
        if index < len(tokens) and tokens[index][0] == kind:
            value = tokens[index][1]
            index += 1
            return value
        raise SyntaxError(f'Expected {kind}, found {tokens[index][0]}')

    def factor():
        nonlocal index
        if tokens[index][0] == 'NUMBER':
            value = expect('NUMBER')
            if value.startswith('0') and value != '0':
                raise SyntaxError(f'Invalid number format: {value}')
            return ('LITERAL', int(value))
        elif tokens[index][0] == 'IDENT':
            return ('IDENT', expect('IDENT'))
        elif tokens[index][1] in '+-':
            op = expect('OP')
            return ('UNARY', op, factor())
        elif tokens[index][1] == '(':
            expect('OP')
            exp = expression()
            expect('OP')
            return exp
        else:
            raise SyntaxError(f'Unexpected token: {tokens[index]}')

    def term():
        node = factor()
        while index < len(tokens) and tokens[index][1] == '*':
            op = expect('OP')
            node = ('BINARY', op, node, factor())
        return node

    def expression():
        node = term()
        while index < len(tokens) and tokens[index][1] in '+-':
            op = expect('OP')
            node = ('BINARY', op, node, term())
        return node

    def assignment():
        ident = expect('IDENT')
        expect('ASSIGN')
        exp = expression()
        expect('END')
        return ('ASSIGN', ident, exp)

    def program():
        statements = []
        while index < len(tokens):
            statements.append(assignment())
        return statements

    index = 0
    return program()

# Evaluate syntax tree
def evaluate(ast, variables):
    def eval_node(node):
        if node[0] == 'LITERAL':
            return node[1]
        elif node[0] == 'IDENT':
            if node[1] not in variables:
                raise NameError(f'Uninitialized variable: {node[1]}')
            return variables[node[1]]
        elif node[0] == 'UNARY':
            op, expr = node[1], node[2]
            value = eval_node(expr)
            return -value if op == '-' else value
        elif node[0] == 'BINARY':
            op, left, right = node[1], node[2], node[3]
            left_val = eval_node(left)
            right_val = eval_node(right)
            if op == '+':
                return left_val + right_val
            elif op == '-':
                return left_val - right_val
            elif op == '*':
                return left_val * right_val
        raise ValueError(f'Unknown node type: {node}')

    for statement in ast:
        if statement[0] == 'ASSIGN':
            ident, expr = statement[1], statement[2]
            variables[ident] = eval_node(expr)
    return variables

# Interperet the program
def interpret(program):
    try:
        tokens = list(tokenize(program))
        ast = parse(tokens)
        variables = {}
        result = evaluate(ast, variables)
        for var, value in result.items():
            print(f'{var} = {value}')
    except (SyntaxError, NameError) as e:
        print('error')

# Example usage
programs = [
    "x = 001;",
    "x_2 = 0;",
    "x = 0 y = x; z = ---(x+y);",
    "x = 1; y = 2; z = ---(x+y)*(x+-y);",
]

for program in programs:
    print(f'Input:\n{program}')
    interpret(program)
    print('-' * 20)
