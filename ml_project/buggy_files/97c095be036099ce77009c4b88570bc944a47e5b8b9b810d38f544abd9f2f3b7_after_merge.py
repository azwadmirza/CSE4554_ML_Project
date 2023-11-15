    def add_link(self, referenced, dependent):
        """Add a link between two relations to the database. If either relation
        does not exist, it will be added as an "external" relation.

        The dependent model refers _to_ the referenced model. So, given
        arguments of (jake_test, bar, jake_test, foo):
        both values are in the schema jake_test and foo is a view that refers
        to bar, so "drop bar cascade" will drop foo and all of foo's
        dependents.

        :param BaseRelation referenced: The referenced model.
        :param BaseRelation dependent: The dependent model.
        :raises InternalError: If either entry does not exist.
        """
        ref_key = _make_key(referenced)
        if (ref_key.database, ref_key.schema) not in self:
            # if we have not cached the referenced schema at all, we must be
            # referring to a table outside our control. There's no need to make
            # a link - we will never drop the referenced relation during a run.
            logger.debug(
                '{dep!s} references {ref!s} but {ref.database}.{ref.schema} '
                'is not in the cache, skipping assumed external relation'
                .format(dep=dependent, ref=ref_key)
            )
            return
        if ref_key not in self.relations:
            # Insert a dummy "external" relation.
            referenced = referenced.replace(
                type=referenced.RelationType.External
            )
            self.add(referenced)

        dep_key = _make_key(dependent)
        if dep_key not in self.relations:
            # Insert a dummy "external" relation.
            dependent = dependent.replace(
                type=referenced.RelationType.External
            )
            self.add(dependent)
        logger.debug(
            'adding link, {!s} references {!s}'.format(dep_key, ref_key)
        )
        with self.lock:
            self._add_link(ref_key, dep_key)