    async def set_type_codec(self, typename, *,
                             schema='public', encoder, decoder,
                             binary=None, format='text'):
        """Set an encoder/decoder pair for the specified data type.

        :param typename:
            Name of the data type the codec is for.

        :param schema:
            Schema name of the data type the codec is for
            (defaults to ``'public'``)

        :param format:
            The type of the argument received by the *decoder* callback,
            and the type of the *encoder* callback return value.

            If *format* is ``'text'`` (the default), the exchange datum is a
            ``str`` instance containing valid text representation of the
            data type.

            If *format* is ``'binary'``, the exchange datum is a ``bytes``
            instance containing valid _binary_ representation of the
            data type.

            If *format* is ``'tuple'``, the exchange datum is a type-specific
            ``tuple`` of values.  The table below lists supported data
            types and their format for this mode.

            +-----------------+---------------------------------------------+
            |  Type           |                Tuple layout                 |
            +=================+=============================================+
            | ``interval``    | (``months``, ``days``, ``microseconds``)    |
            +-----------------+---------------------------------------------+
            | ``date``        | (``date ordinal relative to Jan 1 2000``,)  |
            |                 | ``-2^31`` for negative infinity timestamp   |
            |                 | ``2^31-1`` for positive infinity timestamp. |
            +-----------------+---------------------------------------------+
            | ``timestamp``   | (``microseconds relative to Jan 1 2000``,)  |
            |                 | ``-2^63`` for negative infinity timestamp   |
            |                 | ``2^63-1`` for positive infinity timestamp. |
            +-----------------+---------------------------------------------+
            | ``timestamp     | (``microseconds relative to Jan 1 2000      |
            | with time zone``| UTC``,)                                     |
            |                 | ``-2^63`` for negative infinity timestamp   |
            |                 | ``2^63-1`` for positive infinity timestamp. |
            +-----------------+---------------------------------------------+
            | ``time``        | (``microseconds``,)                         |
            +-----------------+---------------------------------------------+
            | ``time with     | (``microseconds``,                          |
            | time zone``     | ``time zone offset in seconds``)            |
            +-----------------+---------------------------------------------+

        :param encoder:
            Callable accepting a Python object as a single argument and
            returning a value encoded according to *format*.

        :param decoder:
            Callable accepting a single argument encoded according to *format*
            and returning a decoded Python object.

        :param binary:
            **Deprecated**.  Use *format* instead.

        Example:

        .. code-block:: pycon

            >>> import asyncpg
            >>> import asyncio
            >>> import datetime
            >>> from dateutil.relativedelta import relativedelta
            >>> async def run():
            ...     con = await asyncpg.connect(user='postgres')
            ...     def encoder(delta):
            ...         ndelta = delta.normalized()
            ...         return (ndelta.years * 12 + ndelta.months,
            ...                 ndelta.days,
            ...                 ((ndelta.hours * 3600 +
            ...                    ndelta.minutes * 60 +
            ...                    ndelta.seconds) * 1000000 +
            ...                  ndelta.microseconds))
            ...     def decoder(tup):
            ...         return relativedelta(months=tup[0], days=tup[1],
            ...                              microseconds=tup[2])
            ...     await con.set_type_codec(
            ...         'interval', schema='pg_catalog', encoder=encoder,
            ...         decoder=decoder, format='tuple')
            ...     result = await con.fetchval(
            ...         "SELECT '2 years 3 mons 1 day'::interval")
            ...     print(result)
            ...     print(datetime.datetime(2002, 1, 1) + result)
            >>> asyncio.get_event_loop().run_until_complete(run())
            relativedelta(years=+2, months=+3, days=+1)
            2004-04-02 00:00:00

        .. versionadded:: 0.12.0
            Added the ``format`` keyword argument and support for 'tuple'
            format.

        .. versionchanged:: 0.12.0
            The ``binary`` keyword argument is deprecated in favor of
            ``format``.

        """
        self._check_open()

        if binary is not None:
            format = 'binary' if binary else 'text'
            warnings.warn(
                "The `binary` keyword argument to "
                "set_type_codec() is deprecated and will be removed in "
                "asyncpg 0.13.0.  Use the `format` keyword argument instead.",
                DeprecationWarning, stacklevel=2)

        typeinfo = await self.fetchrow(
            introspection.TYPE_BY_NAME, typename, schema)
        if not typeinfo:
            raise ValueError('unknown type: {}.{}'.format(schema, typename))

        oid = typeinfo['oid']
        if typeinfo['kind'] != b'b' or typeinfo['elemtype']:
            raise ValueError(
                'cannot use custom codec on non-scalar type {}.{}'.format(
                    schema, typename))

        self._protocol.get_settings().add_python_codec(
            oid, typename, schema, 'scalar',
            encoder, decoder, format)

        # Statement cache is no longer valid due to codec changes.
        self._drop_local_statement_cache()