    def slice(self, start, stop):
        """Computes the "slice" of the :class:`.Query` represented by
        the given indices and returns the resulting :class:`.Query`.

        The start and stop indices behave like the argument to Python's
        built-in :func:`range` function. This method provides an
        alternative to using ``LIMIT``/``OFFSET`` to get a slice of the
        query.

        For example, ::

            session.query(User).order_by(User.id).slice(1, 3)

        renders as

        .. sourcecode:: sql

           SELECT users.id AS users_id,
                  users.name AS users_name
           FROM users ORDER BY users.id
           LIMIT ? OFFSET ?
           (2, 1)

        .. seealso::

           :meth:`.Query.limit`

           :meth:`.Query.offset`

        """
        if start is not None and stop is not None:
            self._offset = self._offset if self._offset is not None else 0
            if start != 0:
                self._offset += start
            self._limit = stop - start
        elif start is None and stop is not None:
            self._limit = stop
        elif start is not None and stop is None:
            self._offset = self._offset if self._offset is not None else 0
            if start != 0:
                self._offset += start

        if isinstance(self._offset, int) and self._offset == 0:
            self._offset = None