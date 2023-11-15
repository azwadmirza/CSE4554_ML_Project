    def nsmallest(self, n, columns=None, keep="first"):
        def map_func(df, n=n, keep=keep, columns=columns):
            if columns is None:
                return pandas.DataFrame(
                    pandas.Series.nsmallest(df.squeeze(axis=1), n=n, keep=keep)
                )
            return pandas.DataFrame.nsmallest(df, n=n, columns=columns, keep=keep)

        if columns is None:
            new_columns = ["__reduced__"]
        else:
            new_columns = self.columns

        new_modin_frame = self._modin_frame._apply_full_axis(
            axis=0, func=map_func, new_columns=new_columns
        )
        return self.__constructor__(new_modin_frame)