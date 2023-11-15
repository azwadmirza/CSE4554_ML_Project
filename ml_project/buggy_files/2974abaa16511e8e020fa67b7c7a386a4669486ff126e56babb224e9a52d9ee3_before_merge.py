    def get_by_scope_and_name(cls, scope, name):
        """
        Get a key value store given a scope and name.

        :param scope: Scope which the key belongs to.
        :type scope: ``str``

        :param name: Name of the key.
        :type key: ``str``

        :rtype: :class:`KeyValuePairDB` or ``None``
        """
        query_result = cls.impl.query(scope=scope, name=name)

        if not query_result:
            msg = 'The key "%s" does not exist in the StackStorm datastore.'
            raise StackStormDBObjectNotFoundError(msg % name)

        return query_result.first() if query_result else None