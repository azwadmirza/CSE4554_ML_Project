    def __call__(self, left, right):
        empty_left, empty_right = build_empty_df(left.dtypes), build_empty_df(right.dtypes)
        # left should have values to keep columns order.
        gen_left_data = [np.random.rand(1).astype(dt)[0] for dt in left.dtypes]
        empty_left = empty_left.append(pd.DataFrame([gen_left_data], columns=list(empty_left.columns))
                                       .astype(left.dtypes))
        gen_right_data = [np.random.rand(1).astype(dt)[0] for dt in right.dtypes]
        empty_right = empty_right.append(pd.DataFrame([gen_right_data], columns=list(empty_right.columns))
                                         .astype(right.dtypes))
        # this `merge` will check whether the combination of those arguments is valid
        merged = empty_left.merge(empty_right, how=self.how, on=self.on,
                                  left_on=self.left_on, right_on=self.right_on,
                                  left_index=self.left_index, right_index=self.right_index,
                                  sort=self.sort, suffixes=self.suffixes,
                                  copy=self.copy_, indicator=self.indicator, validate=self.validate)

        # the `index_value` doesn't matter.
        index_tokenize_objects = [left, right, self.how, self.left_on,
                                  self.right_on, self.left_index, self.right_index]
        return self.new_dataframe([left, right], shape=(np.nan, merged.shape[1]), dtypes=merged.dtypes,
                                  index_value=parse_index(merged.index, *index_tokenize_objects),
                                  columns_value=parse_index(merged.columns, store_data=True))