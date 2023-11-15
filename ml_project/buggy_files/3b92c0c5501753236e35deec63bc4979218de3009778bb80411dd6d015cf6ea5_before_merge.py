    def from_pandas(cls, df):
        new_index = df.index
        new_columns = df.columns
        # If there is non-trivial index, we put it into columns.
        # That's what we usually have for arrow tables and execution
        # result. Unnamed index is renamed to __index__. Also all
        # columns get 'F_' prefix to handle names unsupported in
        # OmniSci.
        if cls._is_trivial_index(df.index):
            index_cols = None
        else:
            orig_index_names = df.index.names
            orig_df = df

            index_cols = ["__index__" if n is None else n for n in df.index.names]
            df.index.names = index_cols
            df = df.reset_index()

            orig_df.index.names = orig_index_names
        new_dtypes = df.dtypes
        df = df.add_prefix("F_")
        new_parts, new_lengths, new_widths = cls._frame_mgr_cls.from_pandas(df, True)
        return cls(
            new_parts,
            new_index,
            new_columns,
            new_lengths,
            new_widths,
            dtypes=new_dtypes,
            index_cols=index_cols,
        )