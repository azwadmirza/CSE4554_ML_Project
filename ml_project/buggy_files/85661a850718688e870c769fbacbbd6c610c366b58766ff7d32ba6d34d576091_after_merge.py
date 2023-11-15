    def _make_query(self):
        table = Table(self.model._meta.table)
        self.query = self._db.query_class.update(table)
        self.resolve_filters(
            model=self.model,
            q_objects=self.q_objects,
            annotations=self.annotations,
            custom_filters=self.custom_filters,
        )
        # Need to get executor to get correct column_map
        executor = self._db.executor_class(model=self.model, db=self._db)

        for key, value in self.update_kwargs.items():
            field_object = self.model._meta.fields_map.get(key)
            if not field_object:
                raise FieldError("Unknown keyword argument {} for model {}".format(key, self.model))
            if field_object.generated:
                raise IntegrityError("Field {} is generated and can not be updated".format(key))
            if key in self.model._meta.db_fields:
                db_field = self.model._meta.fields_db_projection[key]
                value = executor.column_map[key](value, None)
            elif isinstance(field_object, fields.ForeignKeyField):
                db_field = field_object.source_field
                value = executor.column_map[db_field](value.id, None)
            else:
                raise FieldError("Field {} is virtual and can not be updated".format(key))

            self.query = self.query.set(db_field, value)