# Node comparison operators
# ==
NODE_RES_EQ = 0
# >
NODE_RES_GT = 1
# >=
NODE_RES_GTQ = 2
# <
NODE_RES_LT = 3
# <=
NODE_RES_LTQ = 4

# Node types
NODE_SINGLETYPED = 0
NODE_ENFORCED_DICT = 1


def interpret_node_comp(comp):
    if comp == NODE_RES_EQ:
        return "=="
    elif comp == NODE_RES_GT:
        return ">"
    elif comp == NODE_RES_GTQ:
        return ">="
    elif comp == NODE_RES_LT:
        return "<"
    elif comp == NODE_RES_LTQ:
        return "<="
    return "?"
