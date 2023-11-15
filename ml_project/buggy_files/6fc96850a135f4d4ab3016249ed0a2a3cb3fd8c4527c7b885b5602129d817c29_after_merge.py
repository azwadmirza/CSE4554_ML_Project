    def backmap_value(self, value, mapped_probs, n_values, backmappers):
        if backmappers is None:
            return value

        if value.ndim == 2:  # For multitarget, recursive call by columns
            new_value = np.zeros(value.shape)
            for i, n_value, backmapper in zip(
                    itertools.count(), n_values, backmappers):
                new_value[:, i] = self.backmap_value(
                    value[:, i], mapped_probs[:, i, :], [n_value], [backmapper])
            return new_value

        backmapper = backmappers[0]
        if backmapper is None:
            return value

        value = backmapper(value)
        nans = np.isnan(value)
        if not np.any(nans) or n_values[0] < 2:
            return value
        if mapped_probs is not None:
            value[nans] = np.argmax(mapped_probs[nans], axis=1)
        else:
            value[nans] = np.random.RandomState(0).choice(
                backmapper(np.arange(0, n_values[0] - 1)),
                (np.sum(nans), ))
        return value