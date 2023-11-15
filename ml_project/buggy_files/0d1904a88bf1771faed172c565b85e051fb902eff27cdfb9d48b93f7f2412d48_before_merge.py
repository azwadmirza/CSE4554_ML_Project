    def build_mock_groupby(self, **kwargs):
        in_df = self.inputs[0]
        if self.is_dataframe_obj:
            empty_df = build_empty_df(in_df.dtypes, index=pd.RangeIndex(2))
            obj_dtypes = in_df.dtypes[in_df.dtypes == np.dtype('O')]
            empty_df[obj_dtypes.index] = 'O'
        else:
            if in_df.dtype == np.dtype('O'):
                empty_df = pd.Series('O', index=pd.RangeIndex(2), name=in_df.name, dtype=np.dtype('O'))
            else:
                empty_df = build_empty_series(in_df.dtype, index=pd.RangeIndex(2), name=in_df.name)

        new_kw = self.groupby_params
        new_kw.update(kwargs)
        if new_kw.get('level'):
            new_kw['level'] = 0
        if isinstance(new_kw['by'], list):
            new_by = []
            for v in new_kw['by']:
                if isinstance(v, (Base, Entity)):
                    new_by.append(build_empty_series(v.dtype, index=pd.RangeIndex(2), name=v.name))
                else:
                    new_by.append(v)
            new_kw['by'] = new_by
        return empty_df.groupby(**new_kw)