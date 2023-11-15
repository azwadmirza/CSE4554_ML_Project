    def __init__(self, exprs, rules=None):
        """
        A Scope enables data dependence analysis on a totally ordered sequence
        of expressions.
        """
        exprs = as_tuple(exprs)

        self.reads = {}
        self.writes = {}

        self.initialized = set()

        for i, e in enumerate(exprs):
            # Reads
            for j in retrieve_terminals(e.rhs):
                v = self.reads.setdefault(j.function, [])
                mode = 'RI' if e.is_Increment and j.function is e.lhs.function else 'R'
                v.append(TimedAccess(j, mode, i, e.ispace))

            # Write
            v = self.writes.setdefault(e.lhs.function, [])
            mode = 'WI' if e.is_Increment else 'W'
            v.append(TimedAccess(e.lhs, mode, i, e.ispace))

            # If an increment, we got one implicit read
            if e.is_Increment:
                v = self.reads.setdefault(e.lhs.function, [])
                v.append(TimedAccess(e.lhs, 'RI', i, e.ispace))

            # If writing to a scalar, we have an initialization
            if not e.is_Increment and e.is_scalar:
                self.initialized.add(e.lhs.function)

            # Look up ConditionalDimensions
            for d, v in e.conditionals.items():
                symbols = d.free_symbols | set(retrieve_terminals(v))
                for j in symbols:
                    v = self.reads.setdefault(j.function, [])
                    v.append(TimedAccess(j, 'R', -1, e.ispace))

        # The iteration symbols too
        dimensions = set().union(*[e.dimensions for e in exprs])
        for d in dimensions:
            for i in d._defines_symbols:
                for j in i.free_symbols:
                    v = self.reads.setdefault(j.function, [])
                    v.append(TimedAccess(j, 'R', -1))

        # A set of rules to drive the collection of dependencies
        self.rules = as_tuple(rules)
        assert all(callable(i) for i in self.rules)