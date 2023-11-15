    def visit_unique_constraint(self, constraint):
        text = super(SQLiteDDLCompiler, self).visit_unique_constraint(
            constraint
        )

        on_conflict_clause = constraint.dialect_options["sqlite"][
            "on_conflict"
        ]
        if on_conflict_clause is None and len(constraint.columns) == 1:
            on_conflict_clause = list(constraint)[0].dialect_options["sqlite"][
                "on_conflict_unique"
            ]

        if on_conflict_clause is not None:
            text += " ON CONFLICT " + on_conflict_clause

        return text