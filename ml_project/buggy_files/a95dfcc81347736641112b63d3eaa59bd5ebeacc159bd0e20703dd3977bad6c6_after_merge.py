    def __call__(self, data, attribute):
        if type(data) == SqlTable:
            att = attribute.to_sql()
            quantiles = [(i + 1) / self.n for i in range(self.n - 1)]
            query = data._sql_query(
                ['quantile(%s, ARRAY%s)' % (att, str(quantiles))],
                use_time_sample=1000)
            with data._execute_sql_query(query) as cur:
                points = sorted(set(cur.fetchone()[0]))
        else:
            d = distribution.get_distribution(data, attribute)
            points = _discretize.split_eq_freq(d, self.n)
            # np.unique handles cases in which differences are below precision
            points = list(np.unique(points))
        return Discretizer.create_discretized_var(
            data.domain[attribute], points)