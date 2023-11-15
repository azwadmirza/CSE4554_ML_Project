    def __call__(self, context, typevars):
        oset = typevars[self.target]
        for tp in typevars[self.iterator.name].get():
            if isinstance(tp, types.IterableType):
                oset.add_types(types.UniTuple(dtype=tp.iterator_type.yield_type,
                                              count=self.count))
            elif isinstance(tp, types.Tuple):
                oset.add_types(tp)