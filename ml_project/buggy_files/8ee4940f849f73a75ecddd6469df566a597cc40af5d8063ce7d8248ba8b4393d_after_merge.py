def excepthandler_assigned_stmts(self, node=None, context=None, asspath=None):
    for assigned in node_classes.unpack_infer(self.type):
        if isinstance(assigned, nodes.ClassDef):
            assigned = bases.Instance(assigned)
        yield assigned