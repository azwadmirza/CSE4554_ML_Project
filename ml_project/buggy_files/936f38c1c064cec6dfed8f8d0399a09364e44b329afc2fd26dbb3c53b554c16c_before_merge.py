    def create_for_statement(cls, statement, compiler, **kw):
        self = cls.__new__(cls)

        ext_info = statement.table._annotations["parententity"]
        self.mapper = mapper = ext_info.mapper

        top_level_stmt = compiler.statement

        self.extra_criteria_entities = {}

        extra_criteria_attributes = {}

        for opt in statement._with_options:
            if opt._is_criteria_option:
                opt.get_global_criteria(extra_criteria_attributes)

        new_crit = cls._adjust_for_extra_criteria(
            extra_criteria_attributes, mapper
        )
        if new_crit:
            statement = statement.where(*new_crit)

        if (
            mapper
            and top_level_stmt._annotations.get("synchronize_session", None)
            == "fetch"
            and compiler.dialect.full_returning
        ):
            statement = statement.returning(*mapper.primary_key)

        DeleteDMLState.__init__(self, statement, compiler, **kw)

        return self