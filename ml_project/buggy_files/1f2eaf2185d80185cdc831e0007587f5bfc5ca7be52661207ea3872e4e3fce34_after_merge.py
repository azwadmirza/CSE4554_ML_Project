def with_assigned_stmts(self, node=None, context=None, asspath=None):
    if asspath is None:
        for _, vars in self.items:
            if vars is None:
                continue
            for lst in vars.infer(context):
                if isinstance(lst, (nodes.Tuple, nodes.List)):
                    for item in lst.nodes:
                        yield item