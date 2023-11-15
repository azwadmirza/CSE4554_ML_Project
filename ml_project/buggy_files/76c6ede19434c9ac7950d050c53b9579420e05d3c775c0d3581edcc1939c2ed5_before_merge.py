    def __call__(self, typeinfer):
        with new_error_context("typing of exhaust iter at {0}", self.loc):
            typevars = typeinfer.typevars
            oset = typevars[self.target]
            for tp in typevars[self.iterator.name].get():
                # unpack optional
                tp = tp.type if isinstance(tp, types.Optional) else tp
                if isinstance(tp, types.BaseTuple):
                    if len(tp) == self.count:
                        typeinfer.add_type(self.target, tp, loc=self.loc)
                        break
                    else:
                        raise ValueError("wrong tuple length for %r: "
                                         "expected %d, got %d"
                                         % (self.iterator.name, self.count, len(tp)))
                elif isinstance(tp, types.IterableType):
                    tup = types.UniTuple(dtype=tp.iterator_type.yield_type,
                                         count=self.count)
                    typeinfer.add_type(self.target, tup, loc=self.loc)
                    break
            else:
                raise TypingError("failed to unpack {}".format(tp), loc=self.loc)