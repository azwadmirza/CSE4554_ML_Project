        def _try_mi(k):
            # TODO: what if a level contains tuples??
            loc = self.get_loc(k)
            new_values = series._values[loc]
            new_index = self[loc]
            new_index = maybe_droplevels(new_index, k)
            return Series(new_values, index=new_index, name=series.name)