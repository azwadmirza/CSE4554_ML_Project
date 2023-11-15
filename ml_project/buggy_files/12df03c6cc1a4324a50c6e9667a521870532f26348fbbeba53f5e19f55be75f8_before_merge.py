    def __init__(self, name, *expressions, **kw):
        r"""Construct an index object.

        :param name:
          The name of the index

        :param \*expressions:
          Column expressions to include in the index.   The expressions
          are normally instances of :class:`.Column`, but may also
          be arbitrary SQL expressions which ultimately refer to a
          :class:`.Column`.

        :param unique=False:
            Keyword only argument; if True, create a unique index.

        :param quote=None:
            Keyword only argument; whether to apply quoting to the name of
            the index.  Works in the same manner as that of
            :paramref:`.Column.quote`.

        :param info=None: Optional data dictionary which will be populated
            into the :attr:`.SchemaItem.info` attribute of this object.

            .. versionadded:: 1.0.0

        :param \**kw: Additional keyword arguments not mentioned above are
            dialect specific, and passed in the form
            ``<dialectname>_<argname>``. See the documentation regarding an
            individual dialect at :ref:`dialect_toplevel` for detail on
            documented arguments.

        """
        self.table = table = None

        columns = []
        processed_expressions = []
        for (
            expr,
            column,
            strname,
            add_element,
        ) in self._extract_col_expression_collection(expressions):
            if add_element is not None:
                columns.append(add_element)
            processed_expressions.append(expr)

        self.expressions = processed_expressions
        self.name = quoted_name(name, kw.pop("quote", None))
        self.unique = kw.pop("unique", False)
        _column_flag = kw.pop("_column_flag", False)
        if "info" in kw:
            self.info = kw.pop("info")

        # TODO: consider "table" argument being public, but for
        # the purpose of the fix here, it starts as private.
        if "_table" in kw:
            table = kw.pop("_table")

        self._validate_dialect_kwargs(kw)

        # will call _set_parent() if table-bound column
        # objects are present
        ColumnCollectionMixin.__init__(
            self, *columns, _column_flag=_column_flag
        )

        if table is not None:
            self._set_parent(table)