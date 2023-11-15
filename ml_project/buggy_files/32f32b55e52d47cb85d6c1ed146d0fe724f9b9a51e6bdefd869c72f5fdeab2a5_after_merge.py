    async def reset_type_codec(self, typename, *, schema='public'):
        """Reset *typename* codec to the default implementation.

        :param typename:
            Name of the data type the codec is for.

        :param schema:
            Schema name of the data type the codec is for
            (defaults to ``'public'``)

        .. versionadded:: 0.12.0
        """

        typeinfo = await self.fetchrow(
            introspection.TYPE_BY_NAME, typename, schema)
        if not typeinfo:
            raise ValueError('unknown type: {}.{}'.format(schema, typename))

        oid = typeinfo['oid']

        self._protocol.get_settings().remove_python_codec(
            oid, typename, schema)

        # Statement cache is no longer valid due to codec changes.
        self._drop_local_statement_cache()