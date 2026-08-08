class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self.is_empty():
            return self._items.pop()
        raise IndexError("pop from empty stack")

    def peek(self):
        if not self.is_empty():
            return self._items[-1]
        raise IndexError("peek from empty stack")

    def is_empty(self):
        return len(self._items) == 0

    def __bool__(self):
        return not self.is_empty()
