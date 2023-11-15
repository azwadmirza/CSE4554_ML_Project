    def __init__(self, tfnode=None):
        ParsedNode.__init__(self)
        self.original_node = tfnode
        if tfnode is not None:
            from .parse import parse_attr
            self.name = tfnode.name
            if tfnode.op == 'PlaceholderWithDefault':
                self.op = 'Placeholder'
            else:
                self.op = tfnode.op
            self.inputs = [x for x in tfnode.input if not x.startswith('^')]
            self.control_inputs = [x[1:] for x in tfnode.input if x.startswith('^')]
            self.attr = {k: parse_attr(v) for k, v in tfnode.attr.items()}