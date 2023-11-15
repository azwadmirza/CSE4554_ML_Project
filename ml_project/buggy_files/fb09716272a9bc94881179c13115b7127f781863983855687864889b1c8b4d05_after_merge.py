    def __init__(self, query, column, namespace=None):
        self.expr = column
        self.namespace = namespace
        search_entities = True
        check_column = False

        if isinstance(column, util.string_types):
            util.warn_deprecated(
                "Plain string expression passed to Query() should be "
                "explicitly declared using literal_column(); "
                "automatic coercion of this value will be removed in "
                "SQLAlchemy 1.4"
            )
            column = sql.literal_column(column)
            self._label_name = column.name
            search_entities = False
            check_column = True
            _entity = None
        elif isinstance(
            column, (attributes.QueryableAttribute, interfaces.PropComparator)
        ):
            _entity = getattr(column, "_parententity", None)
            if _entity is not None:
                search_entities = False
            self._label_name = column.key
            column = column._query_clause_element()
            check_column = True
            if isinstance(column, Bundle):
                _BundleEntity(query, column)
                return

        if not isinstance(column, sql.ColumnElement):
            if hasattr(column, "_select_iterable"):
                # break out an object like Table into
                # individual columns
                for c in column._select_iterable:
                    if c is column:
                        break
                    _ColumnEntity(query, c, namespace=column)
                else:
                    return

            raise sa_exc.InvalidRequestError(
                "SQL expression, column, or mapped entity "
                "expected - got '%r'" % (column,)
            )
        elif not check_column:
            self._label_name = getattr(column, "key", None)
            search_entities = True

        self.type = type_ = column.type
        self.use_id_for_hash = not type_.hashable

        # If the Column is unnamed, give it a
        # label() so that mutable column expressions
        # can be located in the result even
        # if the expression's identity has been changed
        # due to adaption.

        if not column._label and not getattr(column, "is_literal", False):
            column = column.label(self._label_name)

        query._entities.append(self)

        self.column = column
        self.froms = set()

        # look for ORM entities represented within the
        # given expression.  Try to count only entities
        # for columns whose FROM object is in the actual list
        # of FROMs for the overall expression - this helps
        # subqueries which were built from ORM constructs from
        # leaking out their entities into the main select construct
        self.actual_froms = list(column._from_objects)
        actual_froms = set(self.actual_froms)

        if not search_entities:
            self.entity_zero = _entity
            if _entity:
                self.entities = [_entity]
                self.mapper = _entity.mapper
            else:
                self.entities = []
                self.mapper = None
            self._from_entities = set(self.entities)
        else:
            all_elements = [
                elem
                for elem in sql_util.surface_column_elements(
                    column, include_scalar_selects=False
                )
                if "parententity" in elem._annotations
            ]

            self.entities = util.unique_list(
                [
                    elem._annotations["parententity"]
                    for elem in all_elements
                    if "parententity" in elem._annotations
                ]
            )

            self._from_entities = set(
                [
                    elem._annotations["parententity"]
                    for elem in all_elements
                    if "parententity" in elem._annotations
                    and actual_froms.intersection(elem._from_objects)
                ]
            )
            if self.entities:
                self.entity_zero = self.entities[0]
                self.mapper = self.entity_zero.mapper
            elif self.namespace is not None:
                self.entity_zero = self.namespace
                self.mapper = None
            else:
                self.entity_zero = None
                self.mapper = None