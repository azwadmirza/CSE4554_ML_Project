    def __call__(self, typeinfer):
        with new_error_context("typing of tuple at {0}", self.loc):
            typevars = typeinfer.typevars
            tsets = [typevars[i.name].get() for i in self.items]
            oset = typevars[self.target]
            for vals in itertools.product(*tsets):
                if vals and all(vals[0] == v for v in vals):
                    tup = types.UniTuple(dtype=vals[0], count=len(vals))
                else:
                    # empty tuples fall here as well
                    tup = types.Tuple(vals)
                assert tup.is_precise()
                typeinfer.add_type(self.target, tup, loc=self.loc)