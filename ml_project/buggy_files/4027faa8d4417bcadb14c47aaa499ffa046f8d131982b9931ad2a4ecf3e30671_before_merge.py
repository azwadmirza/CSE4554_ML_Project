def estimate_fuse_size(ctx, op):
    from ...graph import DAG
    from ...executor import Executor

    chunk = op.outputs[0]
    dag = DAG()
    size_ctx = dict()
    keys = set(c.key for c in chunk.composed)
    for c in chunk.composed:
        dag.add_node(c)
        for inp in c.inputs:
            if inp.key not in keys:
                size_ctx[inp.key] = ctx[inp.key]
            if inp not in dag:
                dag.add_node(inp)
            dag.add_edge(inp, c)

    executor = Executor(storage=size_ctx)
    output_keys = [o.key for o in op.outputs]
    results = executor.execute_graph(dag, output_keys, mock=True, no_intermediate=True)
    ctx.update(zip(output_keys, results))

    # update with the maximal memory cost during the whole execution
    total_mem = sum(ctx[key][1] for key in output_keys)
    if total_mem:
        for key in output_keys:
            r = ctx[key]
            ctx[key] = (r[0], max(r[1], r[1] * executor.mock_max_memory // total_mem))