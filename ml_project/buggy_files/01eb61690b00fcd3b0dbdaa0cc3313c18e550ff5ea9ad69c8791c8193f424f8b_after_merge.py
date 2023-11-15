    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], LoweredEq):
            # origin: LoweredEq(devito.LoweredEq, **kwargs)
            input_expr = args[0]
            expr = sympy.Eq.__new__(cls, *input_expr.args, evaluate=False)
            for i in cls._state:
                setattr(expr, '_%s' % i, kwargs.get(i) or getattr(input_expr, i))
            return expr
        elif len(args) == 1 and isinstance(args[0], Eq):
            # origin: LoweredEq(devito.Eq)
            input_expr = expr = args[0]
        elif len(args) == 2:
            expr = sympy.Eq.__new__(cls, *args, evaluate=False)
            for i in cls._state:
                setattr(expr, '_%s' % i, kwargs.pop(i))
            return expr
        else:
            raise ValueError("Cannot construct LoweredEq from args=%s "
                             "and kwargs=%s" % (str(args), str(kwargs)))

        # Well-defined dimension ordering
        ordering = dimension_sort(expr)

        # Analyze the expression
        mapper = detect_accesses(expr)
        oobs = detect_oobs(mapper)
        conditional_dimensions = [i for i in ordering if i.is_Conditional]

        # Construct Intervals for IterationSpace and DataSpace
        intervals = build_intervals(Stencil.union(*mapper.values()))
        iintervals = []  # iteration Intervals
        dintervals = []  # data Intervals
        for i in intervals:
            d = i.dim
            if d in oobs:
                iintervals.append(i.zero())
                dintervals.append(i)
            else:
                iintervals.append(i.zero())
                dintervals.append(i.zero())

        # Construct the IterationSpace
        iintervals = IntervalGroup(iintervals, relations=ordering.relations)
        iterators = build_iterators(mapper)
        ispace = IterationSpace(iintervals, iterators)

        # Construct the DataSpace
        dintervals.extend([Interval(i, 0, 0) for i in ordering
                           if i not in ispace.dimensions + conditional_dimensions])
        parts = {k: IntervalGroup(build_intervals(v)).add(iintervals)
                 for k, v in mapper.items() if k}
        dspace = DataSpace(dintervals, parts)

        # Construct the conditionals
        conditionals = {}
        for d in conditional_dimensions:
            if d.condition is None:
                conditionals[d] = CondEq(d.parent % d.factor, 0)
            else:
                conditionals[d] = lower_exprs(d.condition)
        conditionals = frozendict(conditionals)

        # Lower all Differentiable operations into SymPy operations
        rhs = diff2sympy(expr.rhs)

        # Finally create the LoweredEq with all metadata attached
        expr = super(LoweredEq, cls).__new__(cls, expr.lhs, rhs, evaluate=False)

        expr._dspace = dspace
        expr._ispace = ispace
        expr._conditionals = conditionals
        expr._reads, expr._writes = detect_io(expr)

        expr._is_Increment = input_expr.is_Increment
        expr._implicit_dims = input_expr.implicit_dims

        return expr