from .node_constants import (
    interpret_node_comp,
    NODE_RES_EQ,
    NODE_RES_GT,
    NODE_RES_GTQ,
    NODE_RES_LT,
    NODE_RES_LTQ,
)


class ParserNode:
    """A node validating a JSON query
    Each node may hold any number of distinct references to other children, and each node may have the ability to raise an error during the traversal
    Said references are only validated in their uniqueness for an individual node. It is possible, though not recommended, to have things like "foo/bar/foo/bar/foo"
    Though creating an ambiguously-looking hierarchy, this is valid because there are no duplicate references
    This is not allowed, however: foo/(bar/foo, bar/(foo, bar))
    Since foo has multiple references to bar, it cannot differentiate user intend and will raise an error
    Each node optionally holds a type and a subtype. A type is an overall definition of an object, I.e, int, str, etc. A subtype is enforced after verifying the correctness of the node's type. It is assumed that if a subtype is specified, then the type is an iterable and can hold other types (the node's subtype)
    Typically, if a subtype is specified, it would roughly be equivalent to type<subtype>
    The subtype match is exhaustive, I.e, all of the items within the Nodes are expected to match the given subtype. This means that if the type of the node was list and the subtype was int, [1, 2, 3] passes while [1, 2, 3.0] fails
    This also means that if a subtype is given, a type must also be presented, as the subtype check is constrained by a node's type
    Multiple pieces of data can be checked at once. Since only dictionaries can have keys, read, children, it is possible to provide an iterable. This naturally will incur further integrity checks
    To avoid unnecessary clutter, a node may choose to ignore the data it receives. This is done by not providing values for either the type or the subtype for the given node. In this case, the node will still propagate data to its children, but it will not carry out any integrity checks
    It is also possible to provide both a callback and the expected value for said callback after specifying values for both node type and subtype. Optionally, one could specify the mode for the callback matching after providing the expected value (See node_constants.py). By default, the node will match for an exact result
    The callback will be invoked with the data as its only argument and the result will be interpreted as described by the constants within node_constants.py
    To begin the traversal, give the node a dictionary with node names as keys. The traversal will continue until no children match the items within the dictionary, at which point the integrity checks will occur"""

    def __init__(
        self,
        node_type=None,
        node_subtype=None,
        clb=None,
        expected_value=None,
        match_mode=NODE_RES_EQ,
    ):
        if node_subtype is not None and node_type is None:
            raise ValueError(
                "Failed to receive the primary type for a node with subtype of %s"
                % node_subtype
            )
        if clb is not None and not callable(clb):
            raise TypeError(
                "The provided callback for node with type %s and subtype %s is not callable"
                % (node_type, node_subtype)
            )
        self.children = {}
        self.node_type = node_type
        self.node_subtype = node_subtype
        self.comparison_clb = clb
        self.expected_value = expected_value
        self.comparison_mode = match_mode

    def child_exists(self, child):
        return child in self.children

    def perform_integrity_check(self, data):
        if self.node_type is not None and not isinstance(data, self.node_type):
            raise TypeError(
                "Failed to enforce base data integrity. Found %s, expected %s"
                % (type(data), self.node_type)
            )
        if self.node_subtype is not None and not all(
            isinstance(t, self.node_subtype) for t in data
        ):
            # Alert user of only offending types
            lst_types = ", ".join(
                set(str(type(t)) for t in data if not isinstance(t, self.node_subtype))
            )
            raise TypeError(
                "Failed to enforce node subtype for node of type %s. Found %s, expected %s"
                % (self.node_type, lst_types, self.node_subtype)
            )
        if self.comparison_clb is not None:
            ret_val = self.comparison_clb(data)
            result = False
            if self.comparison_mode == NODE_RES_EQ:
                result = ret_val == self.expected_value
            elif self.comparison_mode == NODE_RES_GT:
                result = ret_val > self.expected_value
            elif self.comparison_mode == NODE_RES_GTQ:
                result = ret_val >= self.expected_value
            elif self.comparison_mode == NODE_RES_LT:
                result = ret_val < self.expected_value
            elif self.comparison_mode == NODE_RES_LTQ:
                result = ret_val <= self.expected_value
            if not result:
                raise ValueError(
                    "Custom callback result did not match the expected value. %s %s %s"
                    % (
                        ret_val,
                        interpret_node_comp(self.comparison_mode),
                        self.expected_value,
                    )
                )

    def visit(self, data):
        if isinstance(data, dict):
            for k, v in data.items():
                if self.child_exists(k):
                    self.children[k].visit(v)
                else:
                    self.perform_integrity_check(v)
        else:
            self.perform_integrity_check(data)

    def insert_child(self, child_label, child):
        if self.child_exists(child_label):
            raise ValueError(
                'Attempted to insert a nonunique child reference, "%s", into node of type %s and subtype %s'
                % (child_label, self.node_type, self.node_subtype)
            )
        self.children[child_label] = child

    def fetch_child(self, child):
        if not self.child_exists(child):
            raise ValueError('Attempted to fetch a nonexistent child, "%s"' % child)
        return self.children[child]
