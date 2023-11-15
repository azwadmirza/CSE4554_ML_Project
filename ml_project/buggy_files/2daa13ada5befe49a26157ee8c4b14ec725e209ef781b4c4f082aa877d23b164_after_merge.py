    def __repr__(self):
        from pandas.io.formats import console

        num_rows = pandas.get_option("display.max_rows") or 10
        num_cols = pandas.get_option("display.max_columns") or 20
        if pandas.get_option("display.max_columns") is None and pandas.get_option(
            "display.expand_frame_repr"
        ):
            width, _ = console.get_console_size()
            width = min(width, len(self.columns))
            col_counter = 0
            i = 0
            while col_counter < width:
                col_counter += len(str(self.columns[i])) + 1
                i += 1

            num_cols = i
            i = len(self.columns) - 1
            col_counter = 0
            while col_counter < width:
                col_counter += len(str(self.columns[i])) + 1
                i -= 1

            num_cols += len(self.columns) - i
        result = repr(self._build_repr_df(num_rows, num_cols))
        if len(self.index) > num_rows or len(self.columns) > num_cols:
            # The split here is so that we don't repr pandas row lengths.
            return result.rsplit("\n\n", 1)[0] + "\n\n[{0} rows x {1} columns]".format(
                len(self.index), len(self.columns)
            )
        else:
            return result