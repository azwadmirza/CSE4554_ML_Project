def operand_deserializer(value):
    graph = DAG.from_json(value)
    if len(graph) == 1:
        chunks = [list(graph)[0]]
    else:
        chunks = [c for c in graph if not isinstance(c.op, Fetch)]
    op = chunks[0].op
    return _OperandWrapper(op, chunks)