    def render_node(self, node):
        nodename = node.__class__.__name__
        methname = 'render_'+nodename
        try:
            return getattr(self, methname)(node)
        except AttributeError:
            raise
            raise SyntaxError("Unknown syntax: " + nodename)