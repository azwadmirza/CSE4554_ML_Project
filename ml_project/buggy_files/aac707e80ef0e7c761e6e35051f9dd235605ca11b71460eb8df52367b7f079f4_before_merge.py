    def create_for_statement(cls, statement, compiler, **kw):

        self = cls.__new__(cls)

        ext_info = statement.table._annotations["parententity"]

        self.mapper = mapper = ext_info.mapper

        self.extra_criteria_entities = {}

        self._resolved_values = cls._get_resolved_values(mapper, statement)

        extra_criteria_attributes = {}

        for opt in statement._with_options:
            if opt._is_criteria_option:
                opt.get_global_criteria(extra_criteria_attributes)

        if not statement._preserve_parameter_order and statement._values:
            self._resolved_values = dict(self._resolved_values)

        new_stmt = sql.Update.__new__(sql.Update)
        new_stmt.__dict__.update(statement.__dict__)
        new_stmt.table = mapper.local_table

        # note if the statement has _multi_values, these
        # are passed through to the new statement, which will then raise
        # InvalidRequestError because UPDATE doesn't support multi_values
        # right now.
        if statement._ordered_values:
            new_stmt._ordered_values = self._resolved_values
        elif statement._values:
            new_stmt._values = self._resolved_values

        new_crit = cls._adjust_for_extra_criteria(
            extra_criteria_attributes, mapper
        )
        if new_crit:
            new_stmt = new_stmt.where(*new_crit)

        # if we are against a lambda statement we might not be the
        # topmost object that received per-execute annotations
        top_level_stmt = compiler.statement
        if (
            top_level_stmt._annotations.get("synchronize_session", None)
            == "fetch"
            and compiler.dialect.full_returning
        ):
            new_stmt = new_stmt.returning(*mapper.primary_key)

        UpdateDMLState.__init__(self, new_stmt, compiler, **kw)

        return self