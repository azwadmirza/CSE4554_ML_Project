def _batched_select(transaction, query, parameters):
    for start_index in range(0, len(parameters), 900):
        current_batch = parameters[start_index:start_index+900]
        bind = "({})".format(','.join('?' for _ in range(len(current_batch))))
        for result in transaction.execute(query.format(bind), current_batch):
            yield result