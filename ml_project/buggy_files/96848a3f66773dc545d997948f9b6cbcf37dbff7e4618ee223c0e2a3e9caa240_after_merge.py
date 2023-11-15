def _commute(node1, node2):

    if node1.type != "op" or node2.type != "op":
        return False

    if any([nd.name in {"barrier", "snapshot", "measure", "reset", "copy"}
            for nd in [node1, node2]]):
        return False

    if node1.condition or node2.condition:
        return False

    qarg = list(set(node1.qargs + node2.qargs))
    qbit_num = len(qarg)

    qarg1 = [qarg.index(q) for q in node1.qargs]
    qarg2 = [qarg.index(q) for q in node2.qargs]

    id_op = Operator(np.eye(2 ** qbit_num))

    op12 = id_op.compose(node1.op, qargs=qarg1).compose(node2.op, qargs=qarg2)
    op21 = id_op.compose(node2.op, qargs=qarg2).compose(node1.op, qargs=qarg1)

    if_commute = (op12 == op21)

    return if_commute