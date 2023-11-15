    def _replace(self, col):
        PrimaryKeyConstraint._autoincrement_column._reset(self)
        self.columns.replace(col)