    def _add_where(self, fragment):
        if not len(self.where):
            return fragment

        args = [
            self._translate(pred, permit_subquery=True) for pred in self.where
        ]
        clause = functools.reduce(sql.and_, args)
        return fragment.where(clause)