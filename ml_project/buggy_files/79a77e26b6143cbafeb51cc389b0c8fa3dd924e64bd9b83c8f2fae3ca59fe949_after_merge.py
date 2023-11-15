    def __init__(
        self,
        model: "Type[Model]",
        db: "BaseDBAsyncClient",
        prefetch_map=None,
        prefetch_queries=None,
    ) -> None:
        self.model = model
        self.db: "BaseDBAsyncClient" = db
        self.prefetch_map = prefetch_map if prefetch_map else {}
        self._prefetch_queries = prefetch_queries if prefetch_queries else {}

        key = f"{self.db.connection_name}:{self.model._meta.table}"
        if key not in EXECUTOR_CACHE:
            self.regular_columns, columns = self._prepare_insert_columns()
            self.insert_query = self._prepare_insert_statement(columns)

            self.column_map: Dict[str, Callable[[Any, Any], Any]] = {}
            for column in self.regular_columns:
                field_object = self.model._meta.fields_map[column]
                if field_object.__class__ in self.TO_DB_OVERRIDE:
                    self.column_map[column] = partial(
                        self.TO_DB_OVERRIDE[field_object.__class__], field_object
                    )
                else:
                    self.column_map[column] = field_object.to_db_value

            table = Table(self.model._meta.table)
            self.delete_query = str(
                self.model._meta.basequery.where(
                    table[self.model._meta.db_pk_field] == self.Parameter(0)
                ).delete()
            )
            self.update_cache: Dict[str, str] = {}

            EXECUTOR_CACHE[key] = (
                self.regular_columns,
                self.insert_query,
                self.column_map,
                self.delete_query,
                self.update_cache,
            )
        else:
            (
                self.regular_columns,
                self.insert_query,
                self.column_map,
                self.delete_query,
                self.update_cache,
            ) = EXECUTOR_CACHE[key]