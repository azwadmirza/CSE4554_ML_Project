    def _replace(self, col):
        PrimaryKeyConstraint._autoincrement_column._reset(self)
        self.columns.replace(col)

        self.dispatch._sa_event_column_added_to_pk_constraint(self, col)