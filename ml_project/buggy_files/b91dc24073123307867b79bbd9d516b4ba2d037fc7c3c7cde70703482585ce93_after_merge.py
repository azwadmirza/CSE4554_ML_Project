    def reset_index(self, drop):
        if drop:
            exprs = OrderedDict()
            for c in self.columns:
                exprs[c] = self.ref(c)
            return self.__constructor__(
                columns=self.columns,
                dtypes=self._dtypes_for_exprs(exprs),
                op=TransformNode(self, exprs),
                index_cols=None,
                force_execution_mode=self._force_execution_mode,
            )
        else:
            if self._index_cols is None:
                raise NotImplementedError(
                    "default index reset with no drop is not supported"
                )
            # Need to demangle index names.
            exprs = OrderedDict()
            for i, c in enumerate(self._index_cols):
                name = self._index_name(c)
                if name is None:
                    name = f"level_{i}"
                if name in exprs:
                    raise ValueError(f"cannot insert {name}, already exists")
                exprs[name] = self.ref(c)
            for c in self.columns:
                if c in exprs:
                    raise ValueError(f"cannot insert {c}, already exists")
                exprs[c] = self.ref(c)
            new_columns = Index.__new__(Index, data=exprs.keys(), dtype="O")
            return self.__constructor__(
                columns=new_columns,
                dtypes=self._dtypes_for_exprs(exprs),
                op=TransformNode(self, exprs),
                index_cols=None,
                force_execution_mode=self._force_execution_mode,
            )