    def __call__(self, context, typevars):
        oset = typevars[self.target]
        for tp in typevars[self.iterator.name].get():
            if isinstance(tp, types.BaseTuple):
                if len(tp) == self.count:
                    oset.add_types(tp)
            elif isinstance(tp, types.IterableType):
                oset.add_types(types.UniTuple(dtype=tp.iterator_type.yield_type,
                                              count=self.count))