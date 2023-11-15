    def _add_link(self, referenced_key, dependent_key):
        """Add a link between two relations to the database. Both the old and
        new entries must alraedy exist in the database.

        :param _ReferenceKey referenced_key: The key identifying the referenced
            model (the one that if dropped will drop the dependent model).
        :param _ReferenceKey dependent_key: The key identifying the dependent
            model.
        :raises InternalError: If either entry does not exist.
        """
        referenced = self.relations.get(referenced_key)
        if referenced is None:
            dbt.exceptions.raise_cache_inconsistent(
                'in add_link, referenced link key {} not in cache!'
                .format(referenced_key)
            )

        dependent = self.relations.get(dependent_key)
        if dependent is None:
            dbt.exceptions.raise_cache_inconsistent(
                'in add_link, dependent link key {} not in cache!'
                .format(dependent_key)
            )

        referenced.add_reference(dependent)