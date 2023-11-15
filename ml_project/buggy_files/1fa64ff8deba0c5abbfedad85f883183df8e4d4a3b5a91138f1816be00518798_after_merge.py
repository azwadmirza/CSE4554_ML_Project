    def max_min_col_update(self):
        """Determines the maximum and minimum number in each column"""
        # If there are no rows to compute max/min then return
        if self.df.shape[0] == 0:
            return
        max_r = self.df.max(numeric_only=True)
        min_r = self.df.min(numeric_only=True)
        self.max_min_col = list(zip(max_r, min_r))
        if len(self.max_min_col) != self.df.shape[1]:
            # Then it contain complex numbers or other types
            float_intran = self.df.applymap(lambda e: isinstance(e, _sup_nr))
            self.complex_intran = self.df.applymap(lambda e:
                                                   isinstance(e, _sup_com))
            mask = float_intran & (~ self.complex_intran)
            try:
                df_abs = self.df[self.complex_intran].abs()
            except TypeError:
                df_abs = self.df[self.complex_intran]
            max_c = df_abs.max(skipna=True)
            min_c = df_abs.min(skipna=True)
            df_real = self.df[mask]
            max_r = df_real.max(skipna=True)
            min_r = df_real.min(skipna=True)
            self.max_min_col = list(zip(DataFrame([max_c,
                                                   max_r]).max(skipna=True),
                                        DataFrame([min_c,
                                                   min_r]).min(skipna=True)))
        self.max_min_col = [[vmax, vmin-1] if vmax == vmin else [vmax, vmin]
                            for vmax, vmin in self.max_min_col]