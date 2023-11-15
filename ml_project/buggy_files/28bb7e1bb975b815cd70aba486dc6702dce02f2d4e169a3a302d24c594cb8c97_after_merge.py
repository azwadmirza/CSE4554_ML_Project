def import_buffer_to_hst(buf):
    """Import content from buf and return a Hy AST."""
    return HyExpression([HySymbol("do")] + tokenize(buf + "\n"))