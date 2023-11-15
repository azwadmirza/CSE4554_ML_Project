    def reload(self):
        import pandas as pd
        if isinstance(self.source, pd.DataFrame):
            df = self.source
        elif isinstance(self.source, Path):
            filetype = getattr(self, 'filetype', self.source.ext)
            if filetype == 'tsv':
                readfunc = self.read_tsv
            elif filetype == 'jsonl':
                readfunc = partial(pd.read_json, lines=True)
            else:
                readfunc = getattr(pd, 'read_'+filetype) or vd.error('no pandas.read_'+filetype)
            df = readfunc(str(self.source), **options.getall('pandas_'+filetype+'_'))

        # reset the index here
        if type(df.index) is not pd.RangeIndex:
            df = df.reset_index()

        self.columns = []
        for col in (c for c in df.columns if not c.startswith("__vd_")):
            self.addColumn(Column(
                col,
                type=self.dtype_to_type(df[col]),
                getter=self.getValue,
                setter=self.setValue
            ))

        if self.columns[0].name == 'index': # if the df contains an index column
            self.column('index').hide()

        self.rows = DataFrameAdapter(df)
        self._selectedMask = pd.Series(False, index=df.index)
        if df.index.nunique() != df.shape[0]:
            vd.warning("Non-unique index, row selection API may not work or may be incorrect")