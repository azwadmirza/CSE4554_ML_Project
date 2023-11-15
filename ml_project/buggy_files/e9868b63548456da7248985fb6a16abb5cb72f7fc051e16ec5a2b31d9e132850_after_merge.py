    def __call__(self, data, attribute, fixed=None):
        if fixed:
            min, max = fixed[attribute.name]
            points = self._split_eq_width(min, max)
        else:
            if type(data) == SqlTable:
                stats = BasicStats(data, attribute)
                points = self._split_eq_width(stats.min, stats.max)
            else:
                values = data[:, attribute]
                values = values.X if values.X.size else values.Y
                min, max = ut.nanmin(values), ut.nanmax(values)
                points = self._split_eq_width(min, max)
        return Discretizer.create_discretized_var(
            data.domain[attribute], points)