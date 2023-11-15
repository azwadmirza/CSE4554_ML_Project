    def _get_labels_for_sorting(self):
        """
        we categorizing our labels by using the
        available catgories (all, not just observed)
        excluding any missing ones (-1); this is in preparation
        for sorting, where we need to disambiguate that -1 is not
        a valid valid
        """
        from pandas.core.categorical import Categorical

        return [Categorical.from_codes(label,
                                       np.arange(np.array(label).max() + 1,
                                                 dtype=label.dtype),
                                       ordered=True)
                for label in self.labels]