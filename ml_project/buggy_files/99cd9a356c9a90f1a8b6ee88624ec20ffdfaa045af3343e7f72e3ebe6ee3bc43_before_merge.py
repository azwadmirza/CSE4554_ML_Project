    def __call__(self, typeinfer):
        with new_error_context("typing of pair-second at {0}", self.loc):
            typevars = typeinfer.typevars
            oset = typevars[self.target]
            for tp in typevars[self.pair.name].get():
                if not isinstance(tp, types.Pair):
                    # XXX is this an error?
                    continue
                typeinfer.add_type(self.target, tp.second_type, loc=self.loc)