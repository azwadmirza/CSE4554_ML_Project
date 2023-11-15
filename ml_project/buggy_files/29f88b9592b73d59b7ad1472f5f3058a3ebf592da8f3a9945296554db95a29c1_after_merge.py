    def get_update_sql(self, update_fields: Optional[List[str]]) -> str:
        """
        Generates the SQL for updating a model depending on provided update_fields.
        Result is cached for performance.
        """
        key = ",".join(update_fields) if update_fields else ""
        if key in self.update_cache:
            return self.update_cache[key]

        table = Table(self.model._meta.table)
        query = self.db.query_class.update(table)
        count = 0
        for field in update_fields or self.model._meta.fields_db_projection.keys():
            db_field = self.model._meta.fields_db_projection[field]
            field_object = self.model._meta.fields_map[field]
            if not field_object.pk:
                query = query.set(db_field, self.Parameter(count))
                count += 1

        query = query.where(table[self.model._meta.db_pk_field] == self.Parameter(count))

        sql = self.update_cache[key] = query.get_sql()
        return sql