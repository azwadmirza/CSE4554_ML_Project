def from_tileable(tileable, dtype=None, name=None):
    op = IndexDataSource(gpu=tileable.op.gpu, sparse=tileable.issparse(),
                         dtype=dtype)
    return op(inp=tileable, name=name)