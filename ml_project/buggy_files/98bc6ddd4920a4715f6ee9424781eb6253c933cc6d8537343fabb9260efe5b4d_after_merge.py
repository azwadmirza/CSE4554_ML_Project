    def __getitem__(self, index):
        """
        Infinite cyclic indexing of options over the integers,
        looping over the set of defined Cycle objects.
        """
        if len(self.kwargs) == 0:
            return {}

        cycles = {k:v.values for k,v in self.kwargs.items() if isinstance(v, Cycle)}
        options = {}
        for key, values in cycles.items():
            options[key] = values[index % len(values)]

        static = {k:v for k,v in self.kwargs.items() if not isinstance(v, Cycle)}
        return dict(static, **options)