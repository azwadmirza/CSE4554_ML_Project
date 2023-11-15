    def add_link(self, referenced, dependent):
        """Add a link between two relations to the database. Both the old and
        new entries must already exist in the database.

        The dependent model refers _to_ the referenced model. So, given
        arguments of (jake_test, bar, jake_test, foo):
        both values are in the schema jake_test and foo is a view that refers
        to bar, so "drop bar cascade" will drop foo and all of foo's
        dependents.

        :param BaseRelation referenced: The referenced model.
        :param BaseRelation dependent: The dependent model.
        :raises InternalError: If either entry does not exist.
        """
        referenced = _make_key(referenced)
        if (referenced.database, referenced.schema) not in self:
            # if we have not cached the referenced schema at all, we must be
            # referring to a table outside our control. There's no need to make
            # a link - we will never drop the referenced relation during a run.
            logger.debug(
                '{dep!s} references {ref!s} but {ref.database}.{ref.schema} '
                'is not in the cache, skipping assumed external relation'
                .format(dep=dependent, ref=referenced)
            )
            return
        dependent = _make_key(dependent)
        logger.debug(
            'adding link, {!s} references {!s}'.format(dependent, referenced)
        )
        with self.lock:
            self._add_link(referenced, dependent)