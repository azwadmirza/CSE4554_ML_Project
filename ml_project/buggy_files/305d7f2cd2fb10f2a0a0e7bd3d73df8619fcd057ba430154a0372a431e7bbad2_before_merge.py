def evalQuery(graph, query, initBindings, base=None):
    ctx = QueryContext(graph)

    ctx.prologue = query.prologue

    if initBindings:
        for k, v in initBindings.iteritems():
            if not isinstance(k, Variable):
                k = Variable(k)
            ctx[k] = v
        # ctx.push()  # nescessary?

    main = query.algebra

    # import pdb; pdb.set_trace()
    if main.datasetClause:
        if ctx.dataset is None:
            raise Exception(
                "Non-conjunctive-graph doesn't know about " +
                "graphs! Try a query without FROM (NAMED).")

        ctx = ctx.clone()  # or push/pop?

        firstDefault = False
        for d in main.datasetClause:
            if d.default:

                if firstDefault:
                    # replace current default graph
                    dg = ctx.dataset.get_context(BNode())
                    ctx = ctx.pushGraph(dg)
                    firstDefault = True

                ctx.load(d.default, default=True)

            elif d.named:
                g = d.named
                ctx.load(g, default=False)

    return evalPart(ctx, main)