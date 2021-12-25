from .parser_node import ParserNode


class JSONParser:
    """A custom JSON parser
    Operates on data that looks like foo/bar/baz: int and ensures said data is of the promised type
    Begin by adding parser nodes with unique labels for each string of data you wish to verify and then call parse with the actual JSON dictionary"""

    def __init__(self):
        self.parser_nodes = {}

    def add_parser_node(self, label, data_table):
        if label in self.parser_nodes:
            raise ValueError(
                'Attempted to add multiple Nodes to a single label, "%s"' % label
            )
        self.parser_nodes[label] = self._create_nodes_from_table(data_table)

    def _create_nodes_from_path_stem(self, path, args):
        """Builds a chain of nodes exhausting `path`
        as of now, `args` are unpacked and handed to the last node upon creation"""
        if len(path) == 0 or path == "/":
            return ParserNode(*args)
        else:
            paths = path.split("/", 1)
            prev_path = paths[0]
            new_path = paths[1] if len(paths) == 2 else ""
            n = ParserNode()
            n.insert_child(prev_path, self._create_nodes_from_path_stem(new_path, args))
            return n

    def _fetch_last_matching_node_in_path(self, node, path):
        """Traverses until the path produces a nonexistent node"""
        paths = path.split("/", 1)
        child = paths[0]
        new_path = paths[1] if len(paths) == 2 else ""
        if child == "" or not node.child_exists(child):
            return node, path
        else:
            return self._fetch_last_matching_node_in_path(
                node.fetch_child(child), new_path
            )

    def _create_nodes_from_table(self, data_table):
        node_obj = ParserNode()
        for k, v in data_table.items():
            # If this becomes a problem, try and figure out how to add memoization to `self._fetch_last_matching_node_in_path`
            # That or process all the keys with identical stems at once
            # I.e, games/foo, foobar/baz, games/bar could be processed as games/(foo, bar), foobar/baz
            insertion_node, path_stem = self._fetch_last_matching_node_in_path(
                node_obj, k
            )
            # We need a label to insert the new node chain under
            paths = path_stem.split("/", 1)
            label = paths[0]
            path_stem = paths[1] if len(paths) == 2 else ""
            insertion_node.insert_child(
                label, self._create_nodes_from_path_stem(path_stem, v)
            )

        return node_obj

    def parse(self, node_label, data):
        if node_label not in self.parser_nodes:
            raise ValueError(
                'Attempted to verify data with a nonexistent parser node, "%s"'
                % node_label
            )
        self.parser_nodes[node_label].visit(data)
