    def __getitem__(self, key):
        from databricks.koalas.frame import DataFrame
        from databricks.koalas.series import Series

        if self._is_series:
            if isinstance(key, Series) and key._kdf is not self._kdf_or_kser._kdf:
                kdf = self._kdf_or_kser.to_frame()
                kdf["__temp_col__"] = key
                return type(self)(kdf[self._kdf_or_kser.name])[kdf["__temp_col__"]]

            cond, limit, remaining_index = self._select_rows(key)
            if cond is None and limit is None:
                return self._kdf_or_kser

            column_labels = self._internal.column_labels
            column_scols = self._internal.column_scols
            returns_series = True
        else:
            assert self._is_df
            if isinstance(key, tuple):
                if len(key) != 2:
                    raise SparkPandasIndexingError("Only accepts pairs of candidates")
                rows_sel, cols_sel = key
            else:
                rows_sel = key
                cols_sel = None

            if isinstance(rows_sel, Series) and rows_sel._kdf is not self._kdf_or_kser:
                kdf = self._kdf_or_kser.copy()
                kdf["__temp_col__"] = rows_sel
                return type(self)(kdf)[kdf["__temp_col__"], cols_sel][
                    list(self._kdf_or_kser.columns)
                ]

            cond, limit, remaining_index = self._select_rows(rows_sel)
            column_labels, column_scols, returns_series = self._select_cols(cols_sel)

            if cond is None and limit is None and returns_series:
                return self._kdf_or_kser._kser_for(column_labels[0])

        if remaining_index is not None:
            index_scols = self._internal.index_scols[-remaining_index:]
            index_map = self._internal.index_map[-remaining_index:]
        else:
            index_scols = self._internal.index_scols
            index_map = self._internal.index_map

        if self._internal.column_label_names is None:
            column_label_names = None
        else:
            # Manage column index names
            level = column_labels_level(column_labels)
            column_label_names = self._internal.column_label_names[-level:]

        try:
            sdf = self._internal._sdf
            if cond is not None:
                sdf = sdf.drop(NATURAL_ORDER_COLUMN_NAME).filter(cond)
            if limit is not None:
                if limit >= 0:
                    sdf = sdf.limit(limit)
                else:
                    sdf = sdf.limit(sdf.count() + limit)

            sdf = sdf.select(index_scols + column_scols)
        except AnalysisException:
            raise KeyError(
                "[{}] don't exist in columns".format([col._jc.toString() for col in column_scols])
            )

        internal = _InternalFrame(
            sdf=sdf,
            index_map=index_map,
            column_labels=column_labels,
            column_label_names=column_label_names,
        )
        kdf = DataFrame(internal)

        if returns_series:
            kdf_or_kser = Series(kdf._internal.copy(scol=kdf._internal.column_scols[0]), anchor=kdf)
        else:
            kdf_or_kser = kdf

        if remaining_index is not None and remaining_index == 0:
            pdf_or_pser = kdf_or_kser.head(2).to_pandas()
            length = len(pdf_or_pser)
            if length == 0:
                raise KeyError(name_like_string(key))
            elif length == 1:
                return pdf_or_pser.iloc[0]
            else:
                return kdf_or_kser
        else:
            return kdf_or_kser