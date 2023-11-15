    def _set_parent(self, table):
        if not self.name:
            raise exc.ArgumentError(
                "Column must be constructed with a non-blank name or "
                "assign a non-blank .name before adding to a Table."
            )
        if self.key is None:
            self.key = self.name

        existing = getattr(self, "table", None)
        if existing is not None and existing is not table:
            raise exc.ArgumentError(
                "Column object '%s' already assigned to Table '%s'"
                % (self.key, existing.description)
            )

        if self.key in table._columns:
            col = table._columns.get(self.key)
            if col is not self:
                for fk in col.foreign_keys:
                    table.foreign_keys.remove(fk)
                    if fk.constraint in table.constraints:
                        # this might have been removed
                        # already, if it's a composite constraint
                        # and more than one col being replaced
                        table.constraints.remove(fk.constraint)

        table._columns.replace(self)

        self.table = table

        if self.primary_key:
            table.primary_key._replace(self)
        elif self.key in table.primary_key:
            raise exc.ArgumentError(
                "Trying to redefine primary-key column '%s' as a "
                "non-primary-key column on table '%s'"
                % (self.key, table.fullname)
            )

        if self.index:
            if isinstance(self.index, util.string_types):
                raise exc.ArgumentError(
                    "The 'index' keyword argument on Column is boolean only. "
                    "To create indexes with a specific name, create an "
                    "explicit Index object external to the Table."
                )
            table.append_constraint(
                Index(
                    None, self.key, unique=bool(self.unique), _column_flag=True
                )
            )

        elif self.unique:
            if isinstance(self.unique, util.string_types):
                raise exc.ArgumentError(
                    "The 'unique' keyword argument on Column is boolean "
                    "only. To create unique constraints or indexes with a "
                    "specific name, append an explicit UniqueConstraint to "
                    "the Table's list of elements, or create an explicit "
                    "Index object external to the Table."
                )
            table.append_constraint(
                UniqueConstraint(self.key, _column_flag=True)
            )

        self._setup_on_memoized_fks(lambda fk: fk._set_remote_table(table))