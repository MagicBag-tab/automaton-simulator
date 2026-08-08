import copy
from stack import Stack
from node import Node

class Tree:
    def __init__(self, postfix):
        self.root = self._build_tree(postfix)

    def _build_tree(self, postfix):
        if not postfix:
            return None

        stack = Stack()
        tokens = postfix.split()
        
        for token in tokens:
            if token == '.':
                right = stack.pop()
                left = stack.pop()
                stack.push(Node('.', left, right))
            elif token == '|':
                right = stack.pop()
                left = stack.pop()
                stack.push(Node('|', left, right))
            elif token == '*':
                child = stack.pop()
                stack.push(Node('*', child))
            elif token == '+':
                child = stack.pop()
                cloned_child = copy.deepcopy(child)
                star_node = Node('*', cloned_child)
                concat_node = Node('.', child, star_node)
                stack.push(concat_node)
            elif token == '?':
                child = stack.pop()
                epsilon_node = Node('ε')
                or_node = Node('|', child, epsilon_node)
                stack.push(or_node)
            else:
                stack.push(Node(token))
                
        if not stack.is_empty():
            return stack.pop()
        return None
