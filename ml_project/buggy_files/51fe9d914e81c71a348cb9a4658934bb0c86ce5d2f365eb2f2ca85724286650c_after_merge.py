def mulass_assigned_stmts(self, nodes, node=None, context=None, asspath=None):
    if asspath is None:
        asspath = []

    try:
        index = self.elts.index(node)
    except ValueError:
         util.reraise(exceptions.InferenceError(
             'Tried to retrieve a node {node!r} which does not exist',
             node=self, assign_path=asspath, context=context))

    asspath.insert(0, index)
    return self.parent.assigned_stmts(node=self, context=context, asspath=asspath)