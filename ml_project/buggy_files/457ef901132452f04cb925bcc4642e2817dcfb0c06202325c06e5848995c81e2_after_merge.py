    def get_new_columns(self):
        if self.value_columns is None:
            if self.lift == 0:
                return self.removed_level

            lev = self.removed_level
            return lev.insert(0, _get_na_value(lev.dtype.type))

        stride = len(self.removed_level) + self.lift
        width = len(self.value_columns)
        propagator = np.repeat(np.arange(width), stride)
        if isinstance(self.value_columns, MultiIndex):
            new_levels = self.value_columns.levels + (self.removed_level_full,)
            new_names = self.value_columns.names + (self.removed_name,)

            new_labels = [lab.take(propagator)
                          for lab in self.value_columns.labels]
        else:
            new_levels = [self.value_columns, self.removed_level_full]
            new_names = [self.value_columns.name, self.removed_name]
            new_labels = [propagator]

        # The two indices differ only if the unstacked level had unused items:
        if len(self.removed_level_full) != len(self.removed_level):
            # In this case, we remap the new labels to the original level:
            repeater = self.removed_level_full.get_indexer(self.removed_level)
            if self.lift:
                repeater = np.insert(repeater, 0, -1)
        else:
            # Otherwise, we just use each level item exactly once:
            repeater = np.arange(stride) - self.lift

        # The entire level is then just a repetition of the single chunk:
        new_labels.append(np.tile(repeater, width))
        return MultiIndex(levels=new_levels, labels=new_labels,
                          names=new_names, verify_integrity=False)