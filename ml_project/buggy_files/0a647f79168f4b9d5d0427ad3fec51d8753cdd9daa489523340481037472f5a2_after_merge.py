    def get_result(self):
        values, _ = self.get_new_values()
        columns = self.get_new_columns()
        index = self.get_new_index()

        # may need to coerce categoricals here
        if self.is_categorical is not None:
            categories = self.is_categorical.categories
            ordered = self.is_categorical.ordered
            values = [Categorical(values[:, i], categories=categories,
                                  ordered=ordered)
                      for i in range(values.shape[-1])]

        return self.constructor(values, index=index, columns=columns)