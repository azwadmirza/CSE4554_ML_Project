def evalQuery(graph, query, initBindings, base=None):
    ctx = QueryContext(graph)

    ctx.prologue = query.prologue

    main = query.algebra

    if initBindings:
        # add initBindings as a values clause

        values = {} # no dict comprehension in 2.6 :(
        for k,v in initBindings.iteritems():
            if not isinstance(k, Variable):
                k = Variable(k)
            values[k] = v

        main = main.clone() # clone to not change prepared q
        main['p'] = main.p.clone()
        # Find the right place to insert MultiSet join
        repl = main.p
        if repl.name == 'Slice':
            repl['p'] = repl.p.clone()
            repl = repl.p
        if repl.name == 'Distinct':
            repl['p'] = repl.p.clone()
            repl = repl.p
        if repl.p.name == 'OrderBy':
            repl['p'] = repl.p.clone()
            repl = repl.p
        if repl.p.name == 'Extend':
            repl['p'] = repl.p.clone()
            repl = repl.p

        repl['p'] = Join(repl.p, ToMultiSet(Values([values])))

        # TODO: Vars?

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