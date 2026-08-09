import copy

from postfix import BINARY_OPERATORS, UNARY_OPERATORS, RegexSyntaxError, format_token


def tree_steps(postfix_tokens):
    node_stack = []
    nodes = []
    snapshots = []
    next_id = 0

    def create_node(value, kind, left=None, right=None):
        nonlocal next_id
        node = {
            "id": next_id,
            "val": value,
            "type": kind,
            "parent": None,
            "side": None,
            "visible": True,
            "alpha": 0,
            "scale": 0.4,
        }
        next_id += 1
        nodes.append(node)
        if left is not None:
            left["parent"] = node["id"]
            left["side"] = "left"
        if right is not None:
            right["parent"] = node["id"]
            right["side"] = "right"
        return node

    for raw_token in postfix_tokens:
        token = format_token(raw_token)
        if raw_token in BINARY_OPERATORS:
            if len(node_stack) < 2:
                raise RegexSyntaxError(f"Faltan operandos para '{token}'")
            right = node_stack.pop()
            left = node_stack.pop()
            node_stack.append(create_node(token, "operator", left, right))
        elif raw_token in UNARY_OPERATORS:
            if not node_stack:
                raise RegexSyntaxError(f"Falta un operando para '{token}'")
            node_stack.append(create_node(token, "operator", node_stack.pop()))
        else:
            node_stack.append(create_node(token, "operand"))
        snapshots.append({
            "token": token,
            "nodes": copy.deepcopy(nodes),
            "action": f"Procesar '{token}'",
        })
    if len(node_stack) != 1:
        raise RegexSyntaxError("La expresión no produce un árbol válido")
    return snapshots
