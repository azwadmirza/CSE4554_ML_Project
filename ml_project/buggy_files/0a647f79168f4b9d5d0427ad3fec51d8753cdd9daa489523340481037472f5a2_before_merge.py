    def get_result(self):
        # TODO: find a better way than this masking business

        values, value_mask = self.get_new_values()
        columns = self.get_new_columns()
        index = self.get_new_index()

        # filter out missing levels
        if values.shape[1] > 0:
            col_inds, obs_ids = compress_group_index(self.sorted_labels[-1])
            # rare case, level values not observed
            if len(obs_ids) < self.full_shape[1]:
                inds = (value_mask.sum(0) > 0).nonzero()[0]
                values = algos.take_nd(values, inds, axis=1)
                columns = columns[inds]

        # may need to coerce categoricals here
        if self.is_categorical is not None:
            categories = self.is_categorical.categories
            ordered = self.is_categorical.ordered
            values = [Categorical(values[:, i], categories=categories,
                                  ordered=ordered)
                      for i in range(values.shape[-1])]

        return self.constructor(values, index=index, columns=columns)