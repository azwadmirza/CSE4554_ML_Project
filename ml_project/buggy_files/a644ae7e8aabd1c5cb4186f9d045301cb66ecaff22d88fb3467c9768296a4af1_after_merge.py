def assign_assigned_stmts(self, node=None, context=None, asspath=None):
    if not asspath:
        yield self.value
        return
    for inferred in _resolve_asspart(self.value.infer(context), asspath, context):
        yield inferred