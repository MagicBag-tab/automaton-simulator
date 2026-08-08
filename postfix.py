import os
import sys
from tabulate import tabulate

CONCAT = '&'
BINARY_OPERATORS = {'|', '^'}
UNARY_OPERATORS = {'*', '+', '?'}
ALL_OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS | {'(', ')', CONCAT}

def render_table(headers, rows):
    formatted_rows = [
        [row[0], row[1] or 'vacía', row[2] or 'vacío']
        for row in rows
    ]
    return tabulate(
        formatted_rows,
        headers=headers,
        tablefmt='grid',
        stralign='left',
        numalign='left',
    )


def format_token(token):
    return '.' if token == CONCAT else token


def precedence(token):
    if token == '(': 
        return 1
    if token == '|':
        return 2
    if token == CONCAT:
        return 3
    if token in UNARY_OPERATORS:
        return 4
    if token == '^':
        return 5
    return 0


def _is_symbol(token):
    return token not in ALL_OPERATORS or token.startswith('\\')


def add_concatenation(regex):
    regex = regex.replace(' ', '')
    tokens = []
    i = 0

    while i < len(regex):
        if regex[i] == '\\' and i + 1 < len(regex):
            tokens.append(regex[i:i + 2])
            i += 2
        else:
            tokens.append(regex[i])
            i += 1

    formatted = []
    for idx, token in enumerate(tokens):
        formatted.append(token)
        if idx + 1 == len(tokens):
            break

        next_token = tokens[idx + 1]
        if (_is_symbol(token) or token == ')' or token in UNARY_OPERATORS) and (
            _is_symbol(next_token) or next_token == '('
        ):
            formatted.append(CONCAT)

    return formatted


def infix_to_postfix(regex):
    tokens = add_concatenation(regex)
    output = []
    stack = []
    steps = []

    def record_step(action):
        steps.append(
            (
                action,
                ' '.join(format_token(item) for item in stack),
                ' '.join(format_token(item) for item in output),
            )
        )

    for token in tokens:
        if token == '(':
            stack.append(token)
            record_step(format_token(token))
        elif token == ')':
            while stack and stack[-1] != '(': 
                popped = stack.pop()
                output.append(popped)
                record_step(f'pop {format_token(popped)}')
            if stack:
                stack.pop()
                record_step(')')
        elif token in ALL_OPERATORS:
            while stack and stack[-1] != '(' and precedence(stack[-1]) >= precedence(token):
                popped = stack.pop()
                output.append(popped)
                record_step(f'pop {format_token(popped)}')
            stack.append(token)
            record_step(format_token(token))
        else:
            output.append(token)
            record_step(format_token(token))

    while stack:
        popped = stack.pop()
        output.append(popped)
        record_step(f'pop {format_token(popped)}')

    rendered = [format_token(token) for token in output]
    return ' '.join(rendered), steps


def procesar_expresiones(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        print(f"Error: no se encontró el archivo '{nombre_archivo}'")
        return

    with open(nombre_archivo, encoding='utf-8') as archivo:
        for linea in archivo:
            expresion = linea.strip()
            if not expresion:
                continue

            resultado, pasos = infix_to_postfix(expresion)
            print(f"Expresión: {expresion}")
            print(f"Postfix: {resultado}\n")
            print("Pasos realizados:")
            print(render_table(['Token/Acción', 'Pila', 'Postfix'], pasos))
            print("")


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else 'expresiones.txt'
    procesar_expresiones(ruta)


if __name__ == '__main__':
    main()