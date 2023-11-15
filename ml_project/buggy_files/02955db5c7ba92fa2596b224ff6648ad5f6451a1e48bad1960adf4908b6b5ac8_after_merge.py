def for_assigned_stmts(self, node=None, context=None, asspath=None):
    if asspath is None:
        for lst in self.iter.infer(context):
            if isinstance(lst, (nodes.Tuple, nodes.List)):
                for item in lst.elts:
                    yield item
    else:
        for inferred in _resolve_looppart(self.iter.infer(context),
                                         asspath, context):
            yield inferred