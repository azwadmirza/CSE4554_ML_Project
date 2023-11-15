    def get_merge_attributes(self) -> List[str]:
        """
        Returns attributes that will be merged

        Returns
        -------
        List of attributes' to be merged names
        """
        if self.selected_radio.isChecked():
            return self.selected_attributes

        if isinstance(self.data, MArray):
            non_nan = self.data[~self.data.mask]
        elif isinstance(self.data, np.ndarray):
            non_nan = self.data[~np.isnan(self.data)]
        else:  # list
            non_nan = [x for x in self.data if x is not None]

        counts = Counter(non_nan)
        if self.n_values_radio.isChecked():
            keep_values = self.n_values_spin.value()
            values = counts.most_common()[keep_values:]
            indices = [i for i, _ in values]
        elif self.frequent_abs_radio.isChecked():
            indices = [v for v, c in counts.most_common()
                       if c < self.frequent_abs_spin.value()]
        else:  # self.frequent_rel_radio.isChecked():
            n_all = sum(counts.values())
            indices = [v for v, c in counts.most_common()
                       if c / n_all * 100 < self.frequent_rel_spin.value()]

        indices = np.array(indices, dtype=int)  # indices must be ints
        return np.array(self.variable.categories)[indices].tolist()