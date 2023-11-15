    def groups(self):
        """return a list of all the top-level nodes (that are not themselves a
        pandas storage object)
        """
        _tables()
        self._check_if_open()
        return [
            g for g in self._handle.walk_nodes()
            if (getattr(g._v_attrs, 'pandas_type', None) or
                getattr(g, 'table', None) or
                (isinstance(g, _table_mod.table.Table) and
                 g._v_name != u('table')))
        ]