    def __init__(
        self,
        key,
        value=NO_ARG,
        type_=None,
        unique=False,
        required=NO_ARG,
        quote=None,
        callable_=None,
        expanding=False,
        isoutparam=False,
        _compared_to_operator=None,
        _compared_to_type=None,
    ):
        r"""Produce a "bound expression".

        The return value is an instance of :class:`.BindParameter`; this
        is a :class:`.ColumnElement` subclass which represents a so-called
        "placeholder" value in a SQL expression, the value of which is
        supplied at the point at which the statement in executed against a
        database connection.

        In SQLAlchemy, the :func:`.bindparam` construct has
        the ability to carry along the actual value that will be ultimately
        used at expression time.  In this way, it serves not just as
        a "placeholder" for eventual population, but also as a means of
        representing so-called "unsafe" values which should not be rendered
        directly in a SQL statement, but rather should be passed along
        to the :term:`DBAPI` as values which need to be correctly escaped
        and potentially handled for type-safety.

        When using :func:`.bindparam` explicitly, the use case is typically
        one of traditional deferment of parameters; the :func:`.bindparam`
        construct accepts a name which can then be referred to at execution
        time::

            from sqlalchemy import bindparam

            stmt = select([users_table]).\
                        where(users_table.c.name == bindparam('username'))

        The above statement, when rendered, will produce SQL similar to::

            SELECT id, name FROM user WHERE name = :username

        In order to populate the value of ``:username`` above, the value
        would typically be applied at execution time to a method
        like :meth:`.Connection.execute`::

            result = connection.execute(stmt, username='wendy')

        Explicit use of :func:`.bindparam` is also common when producing
        UPDATE or DELETE statements that are to be invoked multiple times,
        where the WHERE criterion of the statement is to change on each
        invocation, such as::

            stmt = (users_table.update().
                    where(user_table.c.name == bindparam('username')).
                    values(fullname=bindparam('fullname'))
                    )

            connection.execute(
                stmt, [{"username": "wendy", "fullname": "Wendy Smith"},
                       {"username": "jack", "fullname": "Jack Jones"},
                       ]
            )

        SQLAlchemy's Core expression system makes wide use of
        :func:`.bindparam` in an implicit sense.   It is typical that Python
        literal values passed to virtually all SQL expression functions are
        coerced into fixed :func:`.bindparam` constructs.  For example, given
        a comparison operation such as::

            expr = users_table.c.name == 'Wendy'

        The above expression will produce a :class:`.BinaryExpression`
        construct, where the left side is the :class:`.Column` object
        representing the ``name`` column, and the right side is a
        :class:`.BindParameter` representing the literal value::

            print(repr(expr.right))
            BindParameter('%(4327771088 name)s', 'Wendy', type_=String())

        The expression above will render SQL such as::

            user.name = :name_1

        Where the ``:name_1`` parameter name is an anonymous name.  The
        actual string ``Wendy`` is not in the rendered string, but is carried
        along where it is later used within statement execution.  If we
        invoke a statement like the following::

            stmt = select([users_table]).where(users_table.c.name == 'Wendy')
            result = connection.execute(stmt)

        We would see SQL logging output as::

            SELECT "user".id, "user".name
            FROM "user"
            WHERE "user".name = %(name_1)s
            {'name_1': 'Wendy'}

        Above, we see that ``Wendy`` is passed as a parameter to the database,
        while the placeholder ``:name_1`` is rendered in the appropriate form
        for the target database, in this case the PostgreSQL database.

        Similarly, :func:`.bindparam` is invoked automatically
        when working with :term:`CRUD` statements as far as the "VALUES"
        portion is concerned.   The :func:`.insert` construct produces an
        ``INSERT`` expression which will, at statement execution time,
        generate bound placeholders based on the arguments passed, as in::

            stmt = users_table.insert()
            result = connection.execute(stmt, name='Wendy')

        The above will produce SQL output as::

            INSERT INTO "user" (name) VALUES (%(name)s)
            {'name': 'Wendy'}

        The :class:`.Insert` construct, at compilation/execution time,
        rendered a single :func:`.bindparam` mirroring the column
        name ``name`` as a result of the single ``name`` parameter
        we passed to the :meth:`.Connection.execute` method.

        :param key:
          the key (e.g. the name) for this bind param.
          Will be used in the generated
          SQL statement for dialects that use named parameters.  This
          value may be modified when part of a compilation operation,
          if other :class:`BindParameter` objects exist with the same
          key, or if its length is too long and truncation is
          required.

        :param value:
          Initial value for this bind param.  Will be used at statement
          execution time as the value for this parameter passed to the
          DBAPI, if no other value is indicated to the statement execution
          method for this particular parameter name.  Defaults to ``None``.

        :param callable\_:
          A callable function that takes the place of "value".  The function
          will be called at statement execution time to determine the
          ultimate value.   Used for scenarios where the actual bind
          value cannot be determined at the point at which the clause
          construct is created, but embedded bind values are still desirable.

        :param type\_:
          A :class:`.TypeEngine` class or instance representing an optional
          datatype for this :func:`.bindparam`.  If not passed, a type
          may be determined automatically for the bind, based on the given
          value; for example, trivial Python types such as ``str``,
          ``int``, ``bool``
          may result in the :class:`.String`, :class:`.Integer` or
          :class:`.Boolean` types being automatically selected.

          The type of a :func:`.bindparam` is significant especially in that
          the type will apply pre-processing to the value before it is
          passed to the database.  For example, a :func:`.bindparam` which
          refers to a datetime value, and is specified as holding the
          :class:`.DateTime` type, may apply conversion needed to the
          value (such as stringification on SQLite) before passing the value
          to the database.

        :param unique:
          if True, the key name of this :class:`.BindParameter` will be
          modified if another :class:`.BindParameter` of the same name
          already has been located within the containing
          expression.  This flag is used generally by the internals
          when producing so-called "anonymous" bound expressions, it
          isn't generally applicable to explicitly-named :func:`.bindparam`
          constructs.

        :param required:
          If ``True``, a value is required at execution time.  If not passed,
          it defaults to ``True`` if neither :paramref:`.bindparam.value`
          or :paramref:`.bindparam.callable` were passed.  If either of these
          parameters are present, then :paramref:`.bindparam.required`
          defaults to ``False``.

        :param quote:
          True if this parameter name requires quoting and is not
          currently known as a SQLAlchemy reserved word; this currently
          only applies to the Oracle backend, where bound names must
          sometimes be quoted.

        :param isoutparam:
          if True, the parameter should be treated like a stored procedure
          "OUT" parameter.  This applies to backends such as Oracle which
          support OUT parameters.

        :param expanding:
          if True, this parameter will be treated as an "expanding" parameter
          at execution time; the parameter value is expected to be a sequence,
          rather than a scalar value, and the string SQL statement will
          be transformed on a per-execution basis to accommodate the sequence
          with a variable number of parameter slots passed to the DBAPI.
          This is to allow statement caching to be used in conjunction with
          an IN clause.

          .. seealso::

            :meth:`.ColumnOperators.in_`

            :ref:`baked_in` - with baked queries

          .. note:: The "expanding" feature does not support "executemany"-
             style parameter sets.

          .. versionadded:: 1.2

          .. versionchanged:: 1.3 the "expanding" bound parameter feature now
             supports empty lists.


        .. seealso::

            :ref:`coretutorial_bind_param`

            :ref:`coretutorial_insert_expressions`

            :func:`.outparam`

        """
        if isinstance(key, ColumnClause):
            type_ = key.type
            key = key.key
        if required is NO_ARG:
            required = value is NO_ARG and callable_ is None
        if value is NO_ARG:
            value = None

        if quote is not None:
            key = quoted_name(key, quote)

        if unique:
            self.key = _anonymous_label(
                "%%(%d %s)s" % (id(self), key or "param")
            )
        else:
            self.key = key or _anonymous_label("%%(%d param)s" % id(self))

        # identifying key that won't change across
        # clones, used to identify the bind's logical
        # identity
        self._identifying_key = self.key

        # key that was passed in the first place, used to
        # generate new keys
        self._orig_key = key or "param"

        self.unique = unique
        self.value = value
        self.callable = callable_
        self.isoutparam = isoutparam
        self.required = required
        self.expanding = expanding

        if type_ is None:
            if _compared_to_type is not None:
                self.type = _compared_to_type.coerce_compared_value(
                    _compared_to_operator, value
                )
            else:
                self.type = type_api._resolve_value_to_type(value)
        elif isinstance(type_, type):
            self.type = type_()
        else:
            self.type = type_