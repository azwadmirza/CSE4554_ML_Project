    def _call(self, x1, x2):
        self._check_inputs(x1, x2)
        if isinstance(x1, DATAFRAME_TYPE) or isinstance(x2, DATAFRAME_TYPE):
            df1, df2 = (x1, x2) if isinstance(x1, DATAFRAME_TYPE) else (x2, x1)
            setattr(self, '_object_type', ObjectType.dataframe)
            kw = self._calc_properties(df1, df2, axis=self.axis)
            if not pd.api.types.is_scalar(df2):
                return self.new_dataframe([x1, x2], **kw)
            else:
                return self.new_dataframe([df1], **kw)
        if isinstance(x1, SERIES_TYPE) or isinstance(x2, SERIES_TYPE):
            s1, s2 = (x1, x2) if isinstance(x1, SERIES_TYPE) else (x2, x1)
            setattr(self, '_object_type', ObjectType.series)
            kw = self._calc_properties(s1, s2)
            if not pd.api.types.is_scalar(s2):
                return self.new_series([x1, x2], **kw)
            else:
                return self.new_series([s1], **kw)
        raise NotImplementedError('Only support add dataframe, series or scalar for now')