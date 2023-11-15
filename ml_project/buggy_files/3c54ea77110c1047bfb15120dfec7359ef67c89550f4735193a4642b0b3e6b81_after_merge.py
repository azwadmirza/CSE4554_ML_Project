def guard(clusters):
    """
    Split Clusters containing conditional expressions into separate Clusters.
    """
    processed = []
    for c in clusters:
        # Group together consecutive expressions with same ConditionalDimensions
        for cds, g in groupby(c.exprs, key=lambda e: tuple(e.conditionals)):
            exprs = list(g)

            if not cds:
                processed.append(c.rebuild(exprs=exprs))
                continue

            # Chain together all conditions from all expressions in `c`
            guards = {}
            for cd in cds:
                condition = guards.setdefault(cd.parent, [])
                for e in exprs:
                    try:
                        condition.append(e.conditionals[cd])
                        break
                    except KeyError:
                        pass
            guards = {d: sympy.And(*v, evaluate=False) for d, v in guards.items()}

            # Construct a guarded Cluster
            processed.append(c.rebuild(exprs=exprs, guards=guards))

    return ClusterGroup(processed)