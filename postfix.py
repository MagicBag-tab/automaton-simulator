import os
import sys
from stack import Stack

CONCAT = '&'
BINARY_OPERATORS = {'|', '^'}
UNARY_OPERATORS = {'*', '+', '?'}
ALL_OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS | {'(', ')', CONCAT}


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
    stack = Stack()

    for token in tokens:
        if token == '(':
            stack.push(token)
        elif token == ')':
            while stack and stack.peek() != '(': 
                popped = stack.pop()
                output.append(popped)
            if stack:
                stack.pop()
        elif token in ALL_OPERATORS:
            while stack and stack.peek() != '(' and precedence(stack.peek()) >= precedence(token):
                popped = stack.pop()
                output.append(popped)
            stack.push(token)
        else:
            output.append(token)

    while stack:
        popped = stack.pop()
        output.append(popped)

    rendered = [format_token(token) for token in output]
    return ' '.join(rendered)

