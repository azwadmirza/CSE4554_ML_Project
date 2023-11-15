def guard(clusters):
    """
    Split Clusters containing conditional expressions into separate Clusters.
    """
    processed = []
    for c in clusters:
        # Group together consecutive expressions with same ConditionalDimensions
        for cds, g in groupby(c.exprs, key=lambda e: e.conditionals):
            exprs = list(g)

            if not cds:
                processed.append(c.rebuild(exprs=exprs))
                continue

            # Create a guarded Cluster
            guards = {}
            for cd in cds:
                condition = guards.setdefault(cd.parent, [])
                if cd.condition is None:
                    condition.append(CondEq(cd.parent % cd.factor, 0))
                else:
                    condition.append(lower_exprs(cd.condition))
            guards = {k: sympy.And(*v, evaluate=False) for k, v in guards.items()}
            exprs = [e.func(*e.args, conditionals=dict(guards)) for e in exprs]
            processed.append(c.rebuild(exprs=exprs, guards=guards))

    return ClusterGroup(processed)